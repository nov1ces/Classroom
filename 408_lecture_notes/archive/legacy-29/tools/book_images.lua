-- Shared print filter for all four books. Images remain editable SVG sources;
-- their PDF siblings are included as vectors in the printed edition.
function Image(img)
  if FORMAT:match('latex') and img.src:match('%.png$') then
    local base = img.src:match('([^/]+)%.png$')
    img.src = 'figures/' .. base .. '.pdf'
  end
  return img
end

function CodeBlock(block)
  if not FORMAT:match('latex') then return block end
  local _, n = block.text:gsub('\n', '\n')
  local start = '\\par\\medskip\\noindent\n'
  local finish = '\\par\\medskip\n'
  -- Long material can break across pages; a short function stays together.
  if n < 32 then
    start = start .. '\\begin{minipage}{\\linewidth}\n'
    finish = '\\end{minipage}' .. finish
  end
  return pandoc.RawBlock('latex', start .. '\\begin{verbatim}\n'
    .. block.text .. '\n\\end{verbatim}\n' .. finish)
end

function Code(code)
  if FORMAT:match('latex') then
    -- A bare initial penalty changes TeX's vertical mode at the start of a
    -- paragraph table cell. Only put breakpoints BETWEEN actual code chunks.
    -- Identifiers/addresses otherwise stay intact.
    local out = {}
    if not code.text:find('[,;]') then
      table.insert(out, code)
      return out
    end
    local chunk = ''
    for i = 1, #code.text do
      local ch = code.text:sub(i,i)
      chunk = chunk .. ch
      if ch == ',' or ch == ';' then
        table.insert(out, pandoc.Code(chunk))
        table.insert(out, pandoc.RawInline('latex', '\\allowbreak{}'))
        chunk = ''
      end
    end
    if #chunk > 0 then table.insert(out, pandoc.Code(chunk)) end
    return out
  end
  return code
end

function Para(p)
  if FORMAT:match('latex') then
    local t = pandoc.utils.stringify(p)
    -- Source markers belong to the first question line, flush with the margin.
    -- Ordinary paragraphs, including those after headings, retain 2em indent.
    if t:match('^【%d%d%d%d】') or t:match('^〖') or t:match('^典型示例（') then
      p.content:insert(1, pandoc.RawInline('latex', '\\noindent{}'))
    end
    if t:match('^解析') or t:match('^解。') then
      return {pandoc.RawBlock('latex', '\\Needspace{6\\baselineskip}'), p}
    end
    if t:match('^对于%s+binary32：$') then
      return {pandoc.RawBlock('latex', '\\Needspace{10\\baselineskip}'), p}
    end
  end
  return p
end

function Header(h)
  if not FORMAT:match('latex') then return h end
  -- Page checks identified these short stems/options as units to keep together.
  -- Reserve the measured room before the heading; long solutions may still flow.
  local space = {
    ['ds-ex1-2']=22, ['ds-ex3-3']=20, ['ds-ex5-4']=18,
    ['ds-ex6-3']=31, ['ds-ex7-1']=18, ['ds-ex8-5']=18,
    ['ds-ex8-8']=18, ['co-ex2-9']=22, ['co-02-07']=23
  }
  local n=space[h.identifier]
  if n then
    return {pandoc.RawBlock('latex', '\\Needspace{' .. n .. '\\baselineskip}'), h}
  end
  return h
end

local table_plan_path = os.getenv('BOOK_TABLE_PLAN')
local table_plan, table_number = nil, 0
if table_plan_path then
  local file = assert(io.open(table_plan_path, 'r'))
  table_plan = pandoc.json.decode(file:read('*a'))
  file:close()
end

local function planned_table(t)
  table_number = table_number + 1
  local plan = assert(table_plan.tables[table_number], 'Missing measured table')
  assert(#t.colspecs == plan.columns, 'Measured table column mismatch')
  local row_number = 0
  local function anchor_row(row)
    row_number = row_number + 1
    for col, cell in ipairs(row.cells) do
      local anchor = pandoc.RawInline('latex', '\\BookTableCellAnchor{' .. plan.id
        .. '-r' .. row_number .. '-c' .. col .. '}')
      if #cell.contents == 0 then
        cell.contents:insert(pandoc.Plain({anchor}))
      else
        local first = cell.contents[1]
        assert(first.tag == 'Plain' or first.tag == 'Para', 'Unsupported measured table cell')
        first.content:insert(1, anchor)
      end
    end
  end
  for _, row in ipairs(t.head.rows) do anchor_row(row) end
  for _, body in ipairs(t.bodies) do
    for _, row in ipairs(body.head) do anchor_row(row) end
    for _, row in ipairs(body.body) do anchor_row(row) end
  end
  for _, row in ipairs(t.foot.rows) do anchor_row(row) end
  assert(row_number == #plan.rows, 'Measured table row mismatch')
  for col = 1, plan.columns do t.colspecs[col] = {pandoc.AlignLeft, 1 / plan.columns} end
  local latex = pandoc.write(pandoc.Pandoc({t}), 'latex', pandoc.WriterOptions({wrap_text='none'}))
  local col = 0
  latex = latex:gsub('p{%(%s*\\columnwidth.-\\real{[%d%.]+}}', function()
    col = col + 1
    return 'p{' .. string.format('%.6fpt', plan.widths_pt[col]) .. '}'
  end)
  assert(col == plan.columns, 'Unexpected Pandoc longtable preamble')
  -- First-page destinations must not be copied with a repeated header box.
  local header_start = assert(latex:find('\\toprule', 1, true))
  local header_end = assert(latex:find('\\endhead', 1, true))
  local repeated = latex:sub(header_start, header_end - 1)
    :gsub('\\BookTableCellAnchor{[^}]+}', '')
  latex = latex:sub(1, header_end - 1) .. '\\endfirsthead\n'
    .. repeated .. latex:sub(header_end)
  local prefix = '\\Needspace{5\\baselineskip}\n'
  if plan.keep_height_pt and plan.keep_height_pt > 0 then
    prefix = '\\Needspace{' .. string.format('%.2fpt', plan.keep_height_pt) .. '}\n'
  end
  local content = pandoc.utils.stringify(t)
  if content:find('本轮乘数低位', 1, true) or content:find('左移后R真值', 1, true) then
    prefix = prefix .. '\\Needspace{14\\baselineskip}\n'
  end
  return pandoc.RawBlock('latex', prefix .. latex)
end

local function length(s)
  local n = 0
  for _, c in utf8.codes(s) do n = n + ((c > 255) and 1.7 or 1) end
  return n
end

function Table(t)
  if table_plan and FORMAT:match('latex') then return planned_table(t) end
  local n = #t.colspecs
  if n == 0 then return t end
  local sums, maxima, counts = {}, {}, {}
  for i = 1, n do sums[i], maxima[i], counts[i] = 0, 0, 0 end
  local function row(r)
    for i, cell in ipairs(r.cells) do
      if i <= n then
        local k = length(pandoc.utils.stringify(cell.contents))
        sums[i] = sums[i] + k
        maxima[i] = math.max(maxima[i], k)
        counts[i] = counts[i] + 1
      end
    end
  end
  for _, r in ipairs(t.head.rows) do row(r) end
  for _, b in ipairs(t.bodies) do
    for _, r in ipairs(b.head) do row(r) end
    for _, r in ipairs(b.body) do row(r) end
  end
  for _, r in ipairs(t.foot.rows) do row(r) end
  local weights, total = {}, 0
  for i = 1, n do
    local mean = sums[i] / math.max(counts[i], 1)
    weights[i] = math.sqrt(math.max(4, mean * .7 + maxima[i] * .3))
    total = total + weights[i]
  end
  local floor = math.min(.13, .65 / n)
  for i = 1, n do
    -- Pandoc prints four decimals. Rounding every column upward can make a
    -- seven-column table wider than the line; truncate to that precision.
    local w = floor + (1 - floor * n) * weights[i] / total
    t.colspecs[i] = {pandoc.AlignLeft, math.floor(w * 10000) / 10000}
  end
  local text=pandoc.utils.stringify(t)
  if FORMAT:match('latex') and (text:find('本轮乘数低位',1,true)
      or text:find('左移后R真值',1,true)) then
    return {pandoc.RawBlock('latex','\\Needspace{14\\baselineskip}'),t}
  end
  return t
end
