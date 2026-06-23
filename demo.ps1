$ErrorActionPreference = "Continue"
$baseUrl = "http://127.0.0.1:5000"

function Show-Step($message) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $message -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Pretty($obj) {
    $obj | ConvertTo-Json -Depth 20
}

Show-Step "1. Checking that Provenance Guard is running"
try {
    $home = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Pretty $home
} catch {
    Write-Host "Could not reach $baseUrl" -ForegroundColor Red
    Write-Host "Start the app first with: python app.py" -ForegroundColor Yellow
    exit
}

Show-Step "2. Submission 1: polished AI-ish sample"
$body1 = @{
    text = "In conclusion, the modern world is a complex tapestry of innovation, creativity, and human ambition. It is important to note that technology continues to reshape the way individuals communicate, create, and imagine the future."
    creator_id = "creator_001"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "$baseUrl/submit" -Method POST -Body $body1 -ContentType "application/json"
Pretty $response1

Show-Step "3. Submission 2: rougher human-style creative sample"
$body2 = @{
    text = "I wrote the first line at 2 a.m. and hated it. Then I kept it anyway, because sometimes the ugly sentence is the only honest one in the room."
    creator_id = "creator_002"
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "$baseUrl/submit" -Method POST -Body $body2 -ContentType "application/json"
Pretty $response2

Show-Step "4. Submission 3: mixed creative sample"
$body3 = @{
    text = "The city moved like a machine, but I still felt human inside it. Every window carried a small blue glow, and every street sounded like someone trying to remember their own name."
    creator_id = "creator_003"
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "$baseUrl/submit" -Method POST -Body $body3 -ContentType "application/json"
Pretty $response3

Show-Step "5. Appeal workflow using the first content_id"
$appeal = @{
    content_id = $response1.content_id
    creator_reasoning = "I wrote this myself and I believe the system may have misread my polished style as AI-generated."
} | ConvertTo-Json

$appealResponse = Invoke-RestMethod -Uri "$baseUrl/appeal" -Method POST -Body $appeal -ContentType "application/json"
Pretty $appealResponse

Show-Step "6. Structured audit log with submissions and appeal"
$log = Invoke-RestMethod -Uri "$baseUrl/log?limit=10" -Method GET
Pretty $log

Show-Step "7. Rate limit proof: repeated submissions until 429 appears"
for ($i = 1; $i -le 12; $i++) {
    $rateBody = @{
        text = "This is rate limit test submission number $i. It is intentionally simple."
        creator_id = "rate_test_user"
    } | ConvertTo-Json

    try {
        $rateResponse = Invoke-RestMethod -Uri "$baseUrl/submit" -Method POST -Body $rateBody -ContentType "application/json"
        Write-Host "Request $i succeeded with confidence $($rateResponse.confidence)"
    } catch {
        Write-Host "Request $i failed as expected." -ForegroundColor Yellow
        Write-Host "Status code:" $_.Exception.Response.StatusCode.value__ -ForegroundColor Yellow
        Write-Host "Message:" $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}

Show-Step "Demo script complete"
Write-Host "You showed: /submit, different confidence scores, transparency labels, both signal scores, /appeal, /log, and rate limiting." -ForegroundColor Green
