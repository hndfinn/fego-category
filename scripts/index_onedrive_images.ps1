param(
    [Parameter(Mandatory = $true)][string]$SourceRoot,
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '../image-library')
)
$ErrorActionPreference = 'Stop'
$root = (Get-Item -LiteralPath $SourceRoot).FullName.TrimEnd('\', '/')
$imageExtensions = @('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif', '.tif', '.tiff', '.bmp', '.gif', '.dng', '.cr2', '.cr3', '.nef', '.arw')
$errors = @()
# Enumerate metadata only. Never open, hash, copy or decode a source file.
$pending = [System.Collections.Generic.Queue[string]]::new()
$pending.Enqueue($root)
$found = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
while ($pending.Count) {
    $directory = $pending.Dequeue()
    foreach ($item in @(Get-ChildItem -LiteralPath $directory -Force -ErrorAction SilentlyContinue -ErrorVariable +errors)) {
        if ($item.PSIsContainer) {
            # OneDrive cloud directories are reparse points; enumerate explicitly.
            # Skip actual symbolic links/junctions to avoid cycles/outside paths.
            if (-not $item.LinkType) { $pending.Enqueue($item.FullName) }
        } elseif ($imageExtensions -contains $item.Extension.ToLowerInvariant()) {
            $found.Add($item)
        }
    }
}
$files = @($found | Sort-Object FullName)
$rows = @($files | ForEach-Object {
    $relative = $_.FullName.Substring($root.Length + 1).Replace('\', '/')
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($relative)) }
    finally { $sha.Dispose() }
    $id = ([System.BitConverter]::ToString($digest)).Replace('-', '').Substring(0, 20).ToLowerInvariant()
    [pscustomobject]@{
        image_id = $id
        relative_path = $relative
        bytes = $_.Length
        modified_utc = $_.LastWriteTimeUtc.ToString('o')
        attributes = $_.Attributes.ToString()
    }
})
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$rows | Export-Csv -LiteralPath (Join-Path $OutputDirectory 'files.csv') -NoTypeInformation -Encoding utf8
$summary = [ordered]@{
    generated_utc = [DateTime]::UtcNow.ToString('o')
    source_folder_name = (Split-Path $root -Leaf)
    source = 'Local OneDrive metadata; correspondence to owner shared folder not yet verified'
    metadata_only = $true
    image_count = $rows.Count
    logical_bytes = ($rows | Measure-Object -Property bytes -Sum).Sum
    enumeration_error_count = $errors.Count
    local_enumeration_complete = ($errors.Count -eq 0)
    remote_completeness_verified = $false
    top_level_groups = @($rows | Group-Object { ($_.relative_path -split '/')[0] } | ForEach-Object {
        [ordered]@{ name = $_.Name; image_count = $_.Count; logical_bytes = ($_.Group | Measure-Object bytes -Sum).Sum }
    })
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'summary.json') -Encoding utf8
if ($errors.Count) {
    Write-Warning 'Some folders could not be enumerated. Index is partial; consult enumeration_error_count.'
}
$summary | ConvertTo-Json -Depth 5
