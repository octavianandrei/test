# This script is for finding folders that have no .XML files and deletes them for faster iteration - 
# maybe it should be added in the py script as a filter

$baseFolder = ".teamcity"
$subfolders = Get-ChildItem -Path $baseFolder -Directory -Recurse

foreach ($folder in $subfolders) {

    $xmlFiles = Get-ChildItem -Path $folder.FullName -Filter *.xml -File -Recurse

    if ($xmlFiles.Count -eq 0) {
        Write-Host "Deleting folder $($folder.FullName)"
        Remove-Item -Path $folder.FullName -Recurse -Force

    } else {
        Write-Host "Folder $($folder.FullName) contains .xml files"
    }
}
Write-Host "Script execution complete"