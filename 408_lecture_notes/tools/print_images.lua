function Image(img)
  if FORMAT:match('latex') and img.src:match('%.png$') then
    img.src = 'figures/' .. img.src:gsub('%.png$', '.pdf')
  end
  return img
end

function CodeBlock(block)
  if FORMAT:match('latex') then
    -- All chapter blocks are shorter than one page. Keep a complete function
    -- together; long examples are split in the editable Markdown at functions.
    local raw = '\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}\n'
      .. '\\begin{verbatim}\n' .. block.text
      .. '\n\\end{verbatim}\n\\end{minipage}\\par\\medskip\n'
    return pandoc.RawBlock('latex', raw)
  end
  return block
end

function Para(p)
  if FORMAT:match('latex') then
    local t = pandoc.utils.stringify(p)
    if t:match('^解析。') then
      return {pandoc.RawBlock('latex', '\\Needspace{6\\baselineskip}'), p}
    elseif t:match('^计数的检查和修改须') then
      return {pandoc.RawBlock('latex', '\\Needspace{8\\baselineskip}'), p}
    end
  end
  return p
end

function Table(t)
  local cols = #t.colspecs
  local first = ''
  if #t.head.rows > 0 and #t.head.rows[1].cells > 0 then
    first = pandoc.utils.stringify(t.head.rows[1].cells[1].contents)
  end
  local widths
  if cols == 2 then
    if first:match('检查项') then widths = {0.19, 0.81}
    else widths = {0.61, 0.39} end
  elseif cols == 3 then
    if first:match('方案') then widths = {0.17, 0.28, 0.55}
    else widths = {0.25, 0.33, 0.42} end
  end
  if widths then
    for i = 1, cols do
      t.colspecs[i] = {pandoc.AlignLeft, widths[i]}
    end
  end
  return t
end
