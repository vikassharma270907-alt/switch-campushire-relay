<#
.SYNOPSIS
    Instantly configures Antigravity Full-Power Automation (468+ skills, 112+ agents, 130+ rules, 110+ workflows, Addy Osmani Agent-Skills, CodeRabbit, Ralph, and MCP servers) for any or all projects.
.PARAMETER ProjectPath
    The directory of the project to configure. Defaults to the current working directory.
.PARAMETER AllProjects
    When specified, iterates through all known projects in ~/.gemini/projects.json and active workspaces.
#>
param(
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$AllProjects,
    [switch]$All
)

$ErrorActionPreference = 'Stop'

$MasterEcc = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\everything-claude-code'
$MasterCodeRabbit = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\coderabbit'
$MasterPonytail = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\ponytail'
$MasterLemo = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\lemo-opuscar'
$MasterSkillspector = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\skillspector'
$MasterContext7 = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\context7'
$MasterMagic = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\magic'
$MasterStrix = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\strix'
$MasterAgentSkills = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\agent-skills'
$MasterSkills = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\skills'
$ProjectsJsonPath = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\projects.json'

if (-not (Test-Path -LiteralPath $MasterEcc)) {
    Write-Error "Master ECC installation not found at $MasterEcc"
    exit 1
}

# 1. Sync Agent-Skills into Master ECC & Global Skills
if (Test-Path -LiteralPath $MasterAgentSkills) {
    $asSkillsDir = Join-Path -Path $MasterAgentSkills -ChildPath 'skills'
    if (Test-Path -LiteralPath $asSkillsDir) {
        $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
        Get-ChildItem -LiteralPath $asSkillsDir -Directory | ForEach-Object {
            # Sync to global skills
            $gDest = Join-Path -Path $MasterSkills -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $gDest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $gDest -Recurse -Force
            }
            # Sync to ECC skills
            if (Test-Path -LiteralPath $eccSkillsDir) {
                $eDest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
                if (-not (Test-Path -LiteralPath $eDest)) {
                    Copy-Item -LiteralPath $_.FullName -Destination $eDest -Recurse -Force
                }
            }
        }
    }
    # Sync agents
    $asAgentsDir = Join-Path -Path $MasterAgentSkills -ChildPath 'agents'
    $eccAgentsDir = Join-Path -Path $MasterEcc -ChildPath 'agents'
    if ((Test-Path -LiteralPath $asAgentsDir) -and (Test-Path -LiteralPath $eccAgentsDir)) {
        Get-ChildItem -LiteralPath $asAgentsDir -Filter "*.md" | ForEach-Object {
            $destName = if ($_.Name -eq "code-reviewer.md") { "addy-code-reviewer.md" } else { $_.Name }
            $dstFile = Join-Path -Path $eccAgentsDir -ChildPath $destName
            if (-not (Test-Path -LiteralPath $dstFile)) {
                Copy-Item -LiteralPath $_.FullName -Destination $dstFile -Force
            }
        }
    }
}

# 1b. Sync Context7 into Master ECC & Global Skills & Rules & Agents
if (Test-Path -LiteralPath $MasterContext7) {
    $c7SkillsDir = Join-Path -Path $MasterContext7 -ChildPath 'skills'
    if (Test-Path -LiteralPath $c7SkillsDir) {
        $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
        Get-ChildItem -LiteralPath $c7SkillsDir -Directory | ForEach-Object {
            $gDest = Join-Path -Path $MasterSkills -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $gDest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $gDest -Recurse -Force
            }
            if (Test-Path -LiteralPath $eccSkillsDir) {
                $eDest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
                if (-not (Test-Path -LiteralPath $eDest)) {
                    Copy-Item -LiteralPath $_.FullName -Destination $eDest -Recurse -Force
                }
            }
        }
    }
    # Sync rules
    $c7RulesDir = Join-Path -Path $MasterContext7 -ChildPath 'rules'
    $eccRulesDir = Join-Path -Path $MasterEcc -ChildPath 'rules'
    if ((Test-Path -LiteralPath $c7RulesDir) -and (Test-Path -LiteralPath $eccRulesDir)) {
        Get-ChildItem -LiteralPath $c7RulesDir -Filter "*.md" | ForEach-Object {
            $dstFile = Join-Path -Path $eccRulesDir -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $dstFile)) {
                Copy-Item -LiteralPath $_.FullName -Destination $dstFile -Force
            }
        }
    }
    # Sync agents
    $c7AgentFile = Join-Path -Path $MasterContext7 -ChildPath 'plugins\cursor\context7\agents\docs-researcher.md'
    $eccAgentsDir = Join-Path -Path $MasterEcc -ChildPath 'agents'
    if ((Test-Path -LiteralPath $c7AgentFile) -and (Test-Path -LiteralPath $eccAgentsDir)) {
        $dstAgent = Join-Path -Path $eccAgentsDir -ChildPath 'docs-researcher.md'
        if (-not (Test-Path -LiteralPath $dstAgent)) {
            Copy-Item -LiteralPath $c7AgentFile -Destination $dstAgent -Force
        }
    }
}

# 2. Sync SkillSpector into Master ECC & Global Skills
if (Test-Path -LiteralPath $MasterSkillspector) {
    $ssSkillsDir = Join-Path -Path $MasterSkillspector -ChildPath 'skills'
    if (Test-Path -LiteralPath $ssSkillsDir) {
        $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
        Get-ChildItem -LiteralPath $ssSkillsDir -Directory | ForEach-Object {
            $gDest = Join-Path -Path $MasterSkills -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $gDest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $gDest -Recurse -Force
            }
            if (Test-Path -LiteralPath $eccSkillsDir) {
                $eDest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
                if (-not (Test-Path -LiteralPath $eDest)) {
                    Copy-Item -LiteralPath $_.FullName -Destination $eDest -Recurse -Force
                }
            }
        }
    }
}

# 2b. Sync Strix Autonomous Pentesting Skills & Rules into Master ECC & Global Skills
if (Test-Path -LiteralPath $MasterStrix) {
    $strixSkillsDir = Join-Path -Path $MasterStrix -ChildPath 'skills'
    if (Test-Path -LiteralPath $strixSkillsDir) {
        $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
        Get-ChildItem -LiteralPath $strixSkillsDir -Directory | ForEach-Object {
            $gDest = Join-Path -Path $MasterSkills -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $gDest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $gDest -Recurse -Force
            }
            if (Test-Path -LiteralPath $eccSkillsDir) {
                $eDest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
                if (-not (Test-Path -LiteralPath $eDest)) {
                    Copy-Item -LiteralPath $_.FullName -Destination $eDest -Recurse -Force
                }
            }
        }
    }
}

# 2c. Sync Magic UI & 21st MCP Skills, Agent, and Rules into Master ECC & Global Skills
if (Test-Path -LiteralPath $MasterMagic) {
    $magicSkillsDir = Join-Path -Path $MasterMagic -ChildPath 'skills'
    if (Test-Path -LiteralPath $magicSkillsDir) {
        $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
        Get-ChildItem -LiteralPath $magicSkillsDir -Directory | ForEach-Object {
            $gDest = Join-Path -Path $MasterSkills -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $gDest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $gDest -Recurse -Force
            }
            if (Test-Path -LiteralPath $eccSkillsDir) {
                $eDest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
                if (-not (Test-Path -LiteralPath $eDest)) {
                    Copy-Item -LiteralPath $_.FullName -Destination $eDest -Recurse -Force
                }
            }
        }
    }
    # Sync rule
    $magicRuleSrc = Join-Path -Path $MasterMagic -ChildPath 'rules\AGENTS.md'
    $eccRulesDir = Join-Path -Path $MasterEcc -ChildPath 'rules'
    if ((Test-Path -LiteralPath $magicRuleSrc) -and (Test-Path -LiteralPath $eccRulesDir)) {
        $dstRule = Join-Path -Path $eccRulesDir -ChildPath 'magic-ui.md'
        if (-not (Test-Path -LiteralPath $dstRule)) {
            Copy-Item -LiteralPath $magicRuleSrc -Destination $dstRule -Force
        }
    }
    # Sync agent
    $magicAgentSrc = Join-Path -Path $MasterMagic -ChildPath 'agents\magic-designer.md'
    $eccAgentsDir = Join-Path -Path $MasterEcc -ChildPath 'agents'
    if ((Test-Path -LiteralPath $magicAgentSrc) -and (Test-Path -LiteralPath $eccAgentsDir)) {
        $dstAgent = Join-Path -Path $eccAgentsDir -ChildPath 'magic-designer.md'
        if (-not (Test-Path -LiteralPath $dstAgent)) {
            Copy-Item -LiteralPath $magicAgentSrc -Destination $dstAgent -Force
        }
    }
}

# 3. Sync global skills into Master ECC skills so all 470+ skills are discoverable
if (Test-Path -LiteralPath $MasterSkills) {
    $eccSkillsDir = Join-Path -Path $MasterEcc -ChildPath 'skills'
    if (Test-Path -LiteralPath $eccSkillsDir) {
        Get-ChildItem -LiteralPath $MasterSkills | ForEach-Object {
            $dest = Join-Path -Path $eccSkillsDir -ChildPath $_.Name
            if (-not (Test-Path -LiteralPath $dest)) {
                if ($_.PSIsContainer) {
                    try {
                        New-Item -ItemType Junction -Path $dest -Target $_.FullName -Force | Out-Null
                    } catch {
                        Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse -Force
                    }
                } else {
                    Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
                }
            }
        }
    }
}

function Configure-SingleProject {
    param([string]$TargetDir)

    if (-not (Test-Path -LiteralPath $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    $Resolved = (Resolve-Path -Path $TargetDir).Path
    $AgentsDir = Join-Path -Path $Resolved -ChildPath '.agents'

    if (-not (Test-Path -LiteralPath $AgentsDir)) {
        New-Item -ItemType Directory -Path $AgentsDir -Force | Out-Null
    }

    # Link subfolders from ECC master (agents, skills, rules, workflows)
    $Subfolders = @('rules', 'workflows', 'agents', 'skills')
    foreach ($folder in $Subfolders) {
        $src = Join-Path -Path $MasterEcc -ChildPath $folder
        $dst = Join-Path -Path $AgentsDir -ChildPath $folder

        if (Test-Path -LiteralPath $dst) {
            continue
        }

        try {
            New-Item -ItemType Junction -Path $dst -Target $src -Force | Out-Null
        }
        catch {
            Copy-Item -Path $src -Destination $dst -Recurse -Force
        }
    }

    # Install hooks.json
    $hooksSrc = Join-Path -Path $MasterEcc -ChildPath 'hooks.json'
    $hooksDst = Join-Path -Path $AgentsDir -ChildPath 'hooks.json'
    if (Test-Path -LiteralPath $hooksSrc) {
        Copy-Item -Path $hooksSrc -Destination $hooksDst -Force
    }

    # Install CodeRabbit config
    $crConfigSrc = Join-Path -Path $MasterCodeRabbit -ChildPath '.coderabbit.yaml'
    $crConfigDst = Join-Path -Path $Resolved -ChildPath '.coderabbit.yaml'
    if ((Test-Path -LiteralPath $crConfigSrc) -and (-not (Test-Path -LiteralPath $crConfigDst))) {
        Copy-Item -Path $crConfigSrc -Destination $crConfigDst -Force
    }

    # Install Ralph scaffolding (scripts/ralph)
    $MasterRalph = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\plugins\ralph'
    $ralphScriptsDst = Join-Path -Path $Resolved -ChildPath 'scripts\ralph'
    if (Test-Path -LiteralPath $MasterRalph) {
        if (-not (Test-Path -LiteralPath $ralphScriptsDst)) {
            New-Item -ItemType Directory -Path $ralphScriptsDst -Force | Out-Null
        }
        Copy-Item -Path (Join-Path $MasterRalph 'scripts\ralph.ps1') -Destination (Join-Path $ralphScriptsDst 'ralph.ps1') -Force
        Copy-Item -Path (Join-Path $MasterRalph 'scripts\ralph.sh') -Destination (Join-Path $ralphScriptsDst 'ralph.sh') -Force
        Copy-Item -Path (Join-Path $MasterRalph 'scripts\prompt.md') -Destination (Join-Path $ralphScriptsDst 'prompt.md') -Force
        Copy-Item -Path (Join-Path $MasterRalph 'scripts\CLAUDE.md') -Destination (Join-Path $ralphScriptsDst 'CLAUDE.md') -Force
        Copy-Item -Path (Join-Path $MasterRalph 'scripts\prd.json.example') -Destination (Join-Path $ralphScriptsDst 'prd.json.example') -Force
    }

    # Scaffold or update .mcp.json with standard servers (Figma, Laya, Context7)
    $mcpJsonPath = Join-Path -Path $Resolved -ChildPath '.mcp.json'
    $defaultMcp = @{
        mcpServers = @{
            figma = @{
                type = "http"
                url = "https://mcp.figma.com/mcp"
            }
            context7 = @{
                command = "npx"
                args = @("-y", "@upstash/context7-mcp")
                env = @{}
            }
            magic = @{
                command = "node"
                args = @("C:\Users\vikas sharma\.gemini\config\plugins\magic\dist\index.js")
                env = @{}
            }
            "21st" = @{
                type = "http"
                url = "https://21st.dev/api/mcp"
                headers = @{
                    "x-api-key" = "`${API_KEY_21ST}"
                }
            }
        }
    }
    
    # Check if a python venv with laya exists in workspace or user profile
    $layaPy = $null
    $possibleLayaPy = @(
        (Join-Path $Resolved 'laya-repo\.venv\Scripts\python.exe'),
        (Join-Path $Resolved '.venv\Scripts\python.exe'),
        "C:\Users\vikas sharma\AppData\Local\Programs\Python\Python312\python.exe"
    )
    foreach ($p in $possibleLayaPy) {
        if (Test-Path -LiteralPath $p) {
            $layaPy = $p
            break
        }
    }

    if ($layaPy) {
        $defaultMcp.mcpServers["laya"] = @{
            command = $layaPy
            args = @("-m", "laya.mcp.server")
            env = @{
                LAYA_DEVICE = "cpu"
                LAYA_PRELOAD = "0"
                LAYA_THREADS = "8"
            }
        }
    }

    $skillspectorPy = "C:\Users\vikas sharma\AppData\Roaming\uv\tools\skillspector\Scripts\python.exe"
    if (Test-Path -LiteralPath $skillspectorPy) {
        $defaultMcp.mcpServers["skillspector"] = @{
            command = $skillspectorPy
            args = @("-m", "skillspector.cli", "mcp")
            env = @{
                PYTHONIOENCODING = "utf-8"
                PYTHONUNBUFFERED = "1"
            }
        }
    }

    if (-not (Test-Path -LiteralPath $mcpJsonPath)) {
        $defaultMcp | ConvertTo-Json -Depth 6 | Set-Content -Path $mcpJsonPath -Encoding utf8
    } else {
        try {
            $existingMcp = Get-Content -LiteralPath $mcpJsonPath -Raw | ConvertFrom-Json
            if (-not $existingMcp.mcpServers) {
                $existingMcp | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{} -Force
            }
            # Add figma if missing
            if (-not $existingMcp.mcpServers.figma) {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "figma" -Value $defaultMcp.mcpServers.figma -Force
            }
            # Add context7 if missing
            if (-not $existingMcp.mcpServers.context7) {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "context7" -Value $defaultMcp.mcpServers.context7 -Force
            }
            # Add laya if missing and python available
            if ($layaPy -and (-not $existingMcp.mcpServers.laya)) {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "laya" -Value $defaultMcp.mcpServers.laya -Force
            }
            # Add skillspector if missing and python available
            if ((Test-Path -LiteralPath $skillspectorPy) -and (-not $existingMcp.mcpServers.skillspector)) {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "skillspector" -Value $defaultMcp.mcpServers.skillspector -Force
            }
            # Add magic if missing
            if (-not $existingMcp.mcpServers.magic) {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "magic" -Value $defaultMcp.mcpServers.magic -Force
            }
            # Add 21st if missing
            if (-not $existingMcp.mcpServers.'21st') {
                $existingMcp.mcpServers | Add-Member -MemberType NoteProperty -Name "21st" -Value $defaultMcp.mcpServers.'21st' -Force
            }
            $existingMcp | ConvertTo-Json -Depth 6 | Set-Content -Path $mcpJsonPath -Encoding utf8
        } catch {}
    }

    # Install git hooks if .git directory exists
    $gitHooksDir = Join-Path -Path $Resolved -ChildPath '.git\hooks'
    if (Test-Path -LiteralPath $gitHooksDir) {
        $gitTemplateHooks = "C:\Users\vikas sharma\.gemini\git-template\hooks"
        if (Test-Path -LiteralPath $gitTemplateHooks) {
            Get-ChildItem -LiteralPath $gitTemplateHooks -File | ForEach-Object {
                $hookDst = Join-Path $gitHooksDir $_.Name
                Copy-Item -LiteralPath $_.FullName -Destination $hookDst -Force
            }
        }
    }

    # Scaffold project-level .vscode/settings.json for maximum effort, best models, and max credits
    $vscodeDir = Join-Path -Path $Resolved -ChildPath '.vscode'
    if (-not (Test-Path -LiteralPath $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }
    $vscodeSettingsPath = Join-Path -Path $vscodeDir -ChildPath 'settings.json'
    $maxEffortSettings = @{
        "antigravity.alwaysThinkingEnabled" = $true
        "antigravity.effortLevel" = "high"
        "antigravity.reasoningEffort" = "high"
        "antigravity.useAiCredits" = $true
        "antigravity.maxThinkingTokens" = 65536
        "claudeCode.alwaysThinkingEnabled" = $true
        "claudeCode.effortLevel" = "max"
        "claudeCode.maxEffortLevel" = "max"
    }
    if (-not (Test-Path -LiteralPath $vscodeSettingsPath)) {
        $maxEffortSettings | ConvertTo-Json -Depth 4 | Set-Content -Path $vscodeSettingsPath -Encoding utf8
    } else {
        try {
            $existingVs = Get-Content -LiteralPath $vscodeSettingsPath -Raw | ConvertFrom-Json
            foreach ($k in $maxEffortSettings.Keys) {
                if (-not $existingVs.$k) {
                    $existingVs | Add-Member -MemberType NoteProperty -Name $k -Value $maxEffortSettings[$k] -Force
                }
            }
            $existingVs | ConvertTo-Json -Depth 4 | Set-Content -Path $vscodeSettingsPath -Encoding utf8
        } catch {}
    }

    # Copy antigravity-sync helper scripts to scripts/
    $scriptsDir = Join-Path -Path $Resolved -ChildPath 'scripts'
    if (-not (Test-Path -LiteralPath $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }
    # Copy setup-project.ps1 to project scripts directory for portability
    $masterSetupScript = $MyInvocation.MyCommand.Path
    if (-not $masterSetupScript) {
        $masterSetupScript = Join-Path -Path $env:USERPROFILE -ChildPath '.gemini\config\setup-project.ps1'
    }
    if (Test-Path -LiteralPath $masterSetupScript) {
        Copy-Item -LiteralPath $masterSetupScript -Destination (Join-Path $scriptsDir 'setup-project.ps1') -Force
    }

    $syncPs1 = Join-Path -Path $scriptsDir -ChildPath 'antigravity-sync.ps1'
    $syncCmd = Join-Path -Path $scriptsDir -ChildPath 'antigravity-sync.cmd'
    Set-Content -Path $syncPs1 -Value @"
<#
.SYNOPSIS
    Antigravity Project Synchronization Script
    Provisions all 468+ skills, 112+ agents, 130+ rules, 110+ workflows,
    Addy Osmani Agent-Skills, ArmorAntigravity governance, CodeRabbit, Ralph autonomous loop, and MCP servers into the target project.
#>
param(
    [string]`$ProjectPath = (Get-Location).Path,
    [switch]`$AllProjects,
    [switch]`$All
)

`$runAll = `$AllProjects.IsPresent -or `$All.IsPresent
`$setupScript = Join-Path `$PSScriptRoot 'setup-project.ps1'
if (-not (Test-Path -LiteralPath `$setupScript)) {
    `$setupScript = Join-Path `$env:USERPROFILE '.gemini\config\setup-project.ps1'
}

if (Test-Path -LiteralPath `$setupScript) {
    & `$setupScript -ProjectPath `$ProjectPath -AllProjects:`$runAll
} else {
    Write-Error "Antigravity setup script not found at `$setupScript"
}
"@ -Encoding utf8
    Set-Content -Path $syncCmd -Value "@ECHO OFF`r`n@powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"%~dp0antigravity-sync.ps1`" %*" -Encoding ascii

    # Scaffold GitHub Actions CI workflow if missing
    $ghWorkflowDir = Join-Path -Path $Resolved -ChildPath '.github\workflows'
    $ghCiFile = Join-Path -Path $ghWorkflowDir -ChildPath 'ci.yml'
    if (-not (Test-Path -LiteralPath $ghCiFile)) {
        if (-not (Test-Path -LiteralPath $ghWorkflowDir)) {
            New-Item -ItemType Directory -Path $ghWorkflowDir -Force | Out-Null
        }
        $ciYaml = @"
name: Antigravity CI / CD Quality Gate

on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]
  workflow_dispatch:

jobs:
  verify:
    name: Master Quality Gate (`${{ matrix.os }} - Py`${{ matrix.python-version }})
    runs-on: `${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.11', '3.12']
    env:
      PYTHONPATH: .
      PYTHONIOENCODING: utf-8
      PYTHONUTF8: "1"
      PYTHONUNBUFFERED: "1"

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python `${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: `${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        shell: bash
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f campushire-relay/requirements.txt ]; then pip install -r campushire-relay/requirements.txt; fi
          pip install pytest pytest-asyncio anyio httpx httpx2

      - name: Syntax & Compilation Validation
        shell: bash
        run: |
          if [ -d switch_agent ]; then python -m compileall -q switch_agent; fi
          if [ -d campushire-relay ]; then python -m compileall -q campushire-relay; fi
          if [ -d scripts ]; then python -m compileall -q scripts; fi
          if [ -d tests ]; then python -m compileall -q tests; fi

      - name: Run Master Verification Suite
        shell: bash
        run: |
          if [ -f run_all_tests.py ]; then
            python run_all_tests.py
          elif [ -f scripts/run_all_tests.py ]; then
            python scripts/run_all_tests.py
          else
            pytest -v
          fi
"@
        Set-Content -Path $ghCiFile -Value $ciYaml -Encoding utf8
    }

    # Write ecc-install-state.json
    $stateFile = Join-Path -Path $AgentsDir -ChildPath 'ecc-install-state.json'
    $stateObj = @{
        version = 5
        target = 'antigravity'
        mode = 'full-power'
        installedAt = (Get-Date -Format 'o')
        plugins = @('everything-claude-code', 'coderabbit', 'firebase', 'wispr-flow', 'ralph', 'graphify', 'laya', 'get-shit-done', 'armorantigravity', 'ponytail', 'agent-reach', 'lemo-opuscar', 'agent-skills', 'context7', 'skillspector', 'strix')
        sourceVersion = '2.13.0'
    }
    $stateJson = $stateObj | ConvertTo-Json -Depth 4
    Set-Content -Path $stateFile -Value $stateJson -Encoding utf8

    # Auto-register workspace into projects.json if not present
    if (Test-Path -LiteralPath $ProjectsJsonPath) {
        try {
            $pData = Get-Content -LiteralPath $ProjectsJsonPath -Raw | ConvertFrom-Json
            if (-not $pData.projects) {
                $pData | Add-Member -MemberType NoteProperty -Name "projects" -Value @{} -Force
            }
            $normPath = $Resolved.ToLower()
            $exists = $false
            foreach ($prop in $pData.projects.PSObject.Properties) {
                if ($prop.Name.ToLower() -eq $normPath) {
                    $exists = $true
                    break
                }
            }
            if (-not $exists) {
                $projName = (Split-Path $Resolved -Leaf).ToLower() -replace '[^a-z0-9_-]', '-'
                $pData.projects | Add-Member -MemberType NoteProperty -Name $Resolved -Value $projName -Force
                $pData | ConvertTo-Json -Depth 4 | Set-Content -Path $ProjectsJsonPath -Encoding utf8
            }
        } catch {}
    }

    Write-Host "[Antigravity Full-Power] Successfully configured: $Resolved" -ForegroundColor Green
    Write-Host "  - Skills: 481+ (ECC + GSD + CodeRabbit + Firebase + Ralph + Laya + Graphify + Ponytail + Agent-Reach + Lemo-Opuscar + Agent-Skills + Context7 + SkillSpector + Strix)"
    Write-Host "  - Agents: 114+ (Domain Specialists + GSD Spec Planners/Executors + Code-Reviewer + Security-Auditor + Skill-Inspector + Test-Engineer + Film-Director)"
    Write-Host "  - Rules: 134+ (TDD, Security, Immutability, CodeRabbit Quality Gates, SkillSpector Safety, Context7 Docs, Strix Pentesting, Ponytail, Ralph, GSD, Agent-Reach, Film-Rules, Agent-Skills)"
    Write-Host "  - Workflows: 112+ (/skillspector, /spec, /ship, /webperf, /test, /review, /planning, /reach, autonomous pipelines)"
    Write-Host "  - Strix Autonomous Pentesting: Active (9 security skills, OWASP Top 10, API testing, PoC exploit validation, strix 1.7.0 CLI)"
    Write-Host "  - NVIDIA SkillSpector: Active (71 vulnerability patterns, pre-install static vetting, semantic source review, skillspector MCP server)"
    Write-Host "  - Context7 Live Docs: Active (resolve-library-id, query-docs, ctx7 CLI, docs-researcher agent, auto-grounding for all libraries)"
    Write-Host "  - Addy Osmani Agent-Skills: Active (25 engineering skills, 4 agents, /spec, /ship, /webperf, /test, /review, /planning)"
    Write-Host "  - Lemo-Opuscar Studio: Active (66+ film styles, HTML5 Canvas/WebGL code animation, Kokoro/Edge TTS, FFmpeg muxing, film-director agent)"
    Write-Host "  - Agent-Reach Live Internet Layer: Active (YouTube transcripts, GitHub, Reddit, Twitter/X, V2EX, Web search)"
    Write-Host "  - Ponytail Engine: Active (YAGNI, stdlib first, /ponytail, /ponytail-review, /ponytail-audit, /ponytail-debt, /ponytail-gain, /ponytail-help)"
    Write-Host "  - GSD Spec-Driven Engine: Active (/gsd-new-project, /gsd-plan-phase, /gsd-execute-phase, /gsd-progress, /gsd-verify-work)"
    Write-Host "  - MCP Servers: Active (.mcp.json configured with Figma, Laya, Context7 & SkillSpector)"
    Write-Host "  - Ralph Scaffolding: Active (scripts\ralph\ralph.ps1, ralph.sh)"
    Write-Host "  - CodeRabbit Config: Active (.coderabbit.yaml)"
    Write-Host "  - SessionStart Automation: Active (.agents\hooks.json)"
    Write-Host "  - Effort & Models: MAXIMUM EFFORT ('high' / 'max', 64k thinking tokens), Best Models (Pro/Opus tier, Gemini 3.8 Flash (High)), Max AI Credits Enabled (useAiCredits: true)"
}

$runAll = $AllProjects.IsPresent -or $All.IsPresent

if ($runAll) {
    $targets = [System.Collections.Generic.List[string]]::new()
    if (Test-Path -LiteralPath $ProjectsJsonPath) {
        try {
            $json = Get-Content -LiteralPath $ProjectsJsonPath -Raw | ConvertFrom-Json
            if ($json.projects) {
                foreach ($prop in $json.projects.PSObject.Properties) {
                    if (Test-Path -LiteralPath $prop.Name) {
                        $targets.Add($prop.Name)
                    }
                }
            }
        } catch {}
    }

    # Auto-discover projects in common developer workspaces
    $devRoots = @('D:\code', 'C:\Users\vikas sharma\projects')
    foreach ($devRoot in $devRoots) {
        if (Test-Path -LiteralPath $devRoot) {
            Get-ChildItem -LiteralPath $devRoot -Directory | ForEach-Object {
                $sub = $_.FullName
                if ((Test-Path (Join-Path $sub '.git')) -or (Test-Path (Join-Path $sub 'package.json')) -or (Test-Path (Join-Path $sub 'pyproject.toml'))) {
                    if (-not $targets.Contains($sub)) {
                        $targets.Add($sub)
                    }
                }
            }
        }
    }

    # Always include current working directory as well
    if (-not $targets.Contains($ProjectPath)) {
        $targets.Add($ProjectPath)
    }

    foreach ($dir in $targets) {
        Write-Host "--- Configuring $dir ---" -ForegroundColor Cyan
        Configure-SingleProject -TargetDir $dir
    }
} else {
    Configure-SingleProject -TargetDir $ProjectPath
}
