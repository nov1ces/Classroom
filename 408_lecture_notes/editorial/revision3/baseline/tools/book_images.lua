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
    -- An address/identifier stays intact, but adjacent inline-code items must
    -- not turn a Chinese list into one unbreakable line.
    local out = {pandoc.RawInline('latex', '\\allowbreak{}')}
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
    ['ds-ex8-8']=18, ['co-ex2-9']=22
  }
  local n=space[h.identifier]
  if n then
    return {pandoc.RawBlock('latex', '\\Needspace{' .. n .. '\\baselineskip}'), h}
  end
  return h
end

local function length(s)
  local n = 0
  for _, c in utf8.codes(s) do n = n + ((c > 255) and 1.7 or 1) end
  return n
end

function Table(t)
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
