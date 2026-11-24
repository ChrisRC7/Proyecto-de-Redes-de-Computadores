$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
  $doc = $word.Documents.Open((Join-Path $dir "Informe.docx"))
  $doc.TablesOfContents(1).Update()
  $doc.Fields.Update() | Out-Null
  $doc.TablesOfContents(1).Update()
  $doc.Save()
  $doc.SaveAs2([ref](Join-Path $dir "Informe.pdf"), [ref]17)
  "Paginas: " + $doc.ComputeStatistics(2)
  $doc.Close($false)
} finally { $word.Quit() }
