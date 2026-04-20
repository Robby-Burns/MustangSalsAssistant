#!/bin/bash
# sync-kernel.sh — Syncs the System Kernel and Framework to all AI tool formats
# Run this whenever agent.md or guide files are updated.
# Usage: ./scripts/sync-kernel.sh
#
# What it does:
#   1. Copies agent.md to tool-specific rule files (Cursor, Claude Code, Windsurf)
#   2. Sets up Antigravity's .agents/ folder with workflows and skills
#   3. Verifies all files are in sync

set -e          # exit on any error
set -u          # treat unset variables as errors (no silent empty expansions)
set -o pipefail # propagate failures through pipes, not just the last command

# ── Bash version guard ────────────────────────────────────────────────────────
# Associative arrays (declare -A) require bash 4+.
# macOS ships bash 3.2 by default. This guard fails loudly instead of silently
# misbehaving mid-script. The AI assistant can propose the right fix for your
# environment when it sees this message.
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo ""
    echo "❌ sync-kernel.sh requires bash 4 or higher."
    echo "   Your version: ${BASH_VERSION}"
    echo ""
    echo "   Options:"
    echo "     Mac (Homebrew):  brew install bash"
    echo "     Mac (manual):    See https://itnext.io/upgrading-bash-on-macos"
    echo "     Linux:           bash is almost certainly 4+ already (check: bash --version)"
    echo "     CI:              Use 'runs-on: ubuntu-latest' — bash 5+ included"
    echo ""
    echo "   Or ask your AI assistant to rewrite this for your environment's stack."
    exit 1
fi
# ─────────────────────────────────────────────────────────────────────────────

KERNEL="agent.md"
GUIDES_DIR="docs/guides"
SKILLS_DIR="skills"

# Tool-specific rule files (Cursor, Claude Code, Windsurf)
TOOL_TARGETS=(".cursorrules" "CLAUDE.md" ".windsurfrules")

# Antigravity paths
AGY_ROOT=".agents"
AGY_WORKFLOWS="$AGY_ROOT/workflows"
AGY_SKILLS="$AGY_ROOT/skills"

echo "🔄 AI Agent Framework — Kernel Sync"
echo "====================================="
echo ""

# ─────────────────────────────────────────────────
# STEP 1: Sync kernel to tool-specific rule files
# ─────────────────────────────────────────────────
if [ ! -f "$KERNEL" ]; then
    echo "❌ Error: $KERNEL not found in project root."
    echo "   Run this script from the project root directory."
    exit 1
fi

echo "📋 Step 1: Syncing kernel to tool-specific files..."
for target in "${TOOL_TARGETS[@]}"; do
    cp "$KERNEL" "$target"
    echo "   ✅ $target"
done
echo ""

# ─────────────────────────────────────────────────
# STEP 2: Set up Antigravity .agents/ structure
# ─────────────────────────────────────────────────
echo "🚀 Step 2: Setting up Antigravity .agents/ structure..."

# Create directories
mkdir -p "$AGY_WORKFLOWS"
mkdir -p "$AGY_SKILLS"

# Copy kernel as a workflow (always available to Antigravity)
cp "$KERNEL" "$AGY_WORKFLOWS/agent-kernel.md"
echo "   ✅ $AGY_WORKFLOWS/agent-kernel.md (kernel)"

# Copy guide files to workflows
if [ -d "$GUIDES_DIR" ]; then
    for guide in "$GUIDES_DIR"/*.md; do
        if [ -f "$guide" ]; then
            filename=$(basename "$guide")
            cp "$guide" "$AGY_WORKFLOWS/$filename"
            echo "   ✅ $AGY_WORKFLOWS/$filename"
        fi
    done
else
    echo "   ⚠️  $GUIDES_DIR not found — skipping guide sync."
    echo "      Create $GUIDES_DIR and place your 00-09 guide files there."
fi

# ─────────────────────────────────────────────────
# AgentSpec discovery: find any *AgentSpec*.md file
#
# Naming convention: [ProjectName]AgentSpec.md, AgentSpec.md, agentspec.md, etc.
# e.g. MustangAgentSpec.md, PhoenixAgentSpec.md, agentspec.md — all valid.
#
# Search locations and priority (highest → lowest):
#   1. docs/                    conventional home for mature/committed specs
#   2. .agents/                 Antigravity project root (hand-placed or tool-generated)
#   3. project root             common during early development
#   4. .agents/workflows/       OUTPUT of this script — never treated as a source.
#                               If the only copy found is here, it means the source was
#                               deleted. A warning is printed; the orphan is left in place.
#
# Same-filename collision rule:
#   If the same filename exists in multiple SOURCE locations (1–3) with different content,
#   the script halts that file's sync and prints resolution steps. It does not guess.
#   If content is identical, the highest-priority copy wins silently.
#
# Multi-spec projects:
#   Different filenames (e.g. MustangAgentSpec.md + PhoenixAgentSpec.md) are all synced.
#   Antigravity loads all workflow files semantically — multiple specs coexist fine.
# ─────────────────────────────────────────────────

DOCS_SPECS=()
AGENTS_ROOT_SPECS=()
ROOT_SPECS=()
WORKFLOWS_SPECS=()

while IFS= read -r f; do
    DOCS_SPECS+=("$f")
done < <(find docs -maxdepth 1 -iname "*agentspec*.md" 2>/dev/null | sort)

while IFS= read -r f; do
    AGENTS_ROOT_SPECS+=("$f")
done < <(find .agents -maxdepth 1 -iname "*agentspec*.md" 2>/dev/null | sort)

while IFS= read -r f; do
    ROOT_SPECS+=("$f")
done < <(find . -maxdepth 1 -iname "*agentspec*.md" 2>/dev/null | sort | sed 's|^\./||')

while IFS= read -r f; do
    WORKFLOWS_SPECS+=("$f")
done < <(find "$AGY_WORKFLOWS" -maxdepth 1 -iname "*agentspec*.md" 2>/dev/null | sort)

# All source candidates (priority order, workflows excluded as source)
ALL_SOURCE_SPECS=("${DOCS_SPECS[@]}" "${AGENTS_ROOT_SPECS[@]}" "${ROOT_SPECS[@]}")

# Build a map: filename → canonical source path (highest priority wins)
# Uses an associative array keyed by basename
declare -A SPEC_MAP        # filename → chosen source path
declare -A SPEC_COLLISION  # filename → "yes" if a collision was found

for spec in "${ALL_SOURCE_SPECS[@]}"; do
    name=$(basename "$spec")
    if [ -z "${SPEC_MAP[$name]+_}" ]; then
        # First time seeing this filename — claim it
        SPEC_MAP["$name"]="$spec"
    else
        # Already seen — compare content
        existing="${SPEC_MAP[$name]}"
        if ! diff -q "$existing" "$spec" > /dev/null 2>&1; then
            # Different content: collision
            SPEC_COLLISION["$name"]="yes"
        fi
        # If content is identical, keep the higher-priority copy already in the map
    fi
done

COLLISION_FOUND=false
SYNCED_COUNT=0

if [ ${#SPEC_MAP[@]} -eq 0 ]; then
    # No source specs found anywhere — check if orphan copies exist in workflows/
    if [ ${#WORKFLOWS_SPECS[@]} -gt 0 ]; then
        echo "   ⚠️  No source AgentSpec found in docs/, .agents/, or project root."
        echo "      Orphaned copies exist in $AGY_WORKFLOWS/ from a previous sync:"
        for wf in "${WORKFLOWS_SPECS[@]}"; do
            echo "      • $(basename "$wf")"
        done
        echo "      These will not be re-synced. If the source was deleted intentionally,"
        echo "      remove the orphan(s) from $AGY_WORKFLOWS/ manually."
        echo "      To create a new spec: MASTER_AGENT_DISCOVERY_PROMPT.md"
    else
        echo "   ⚠️  No *AgentSpec*.md found in docs/, .agents/, project root, or $AGY_WORKFLOWS/."
        echo "      Generate one using MASTER_AGENT_DISCOVERY_PROMPT.md"
        echo "      Naming convention: [ProjectName]AgentSpec.md (e.g. MustangAgentSpec.md)"
    fi
else
    for name in "${!SPEC_MAP[@]}"; do
        if [ "${SPEC_COLLISION[$name]+_}" ]; then
            # Collision — list all conflicting locations and halt this file
            echo ""
            echo "   ⚠️  ─────────────────────────────────────────────────────"
            echo "   ⚠️  AGENTSPEC COLLISION: $name found in multiple locations with different content."
            echo "   ⚠️  Conflicting copies:"
            for spec in "${ALL_SOURCE_SPECS[@]}"; do
                [ "$(basename "$spec")" = "$name" ] && echo "   ⚠️    • $spec"
            done
            echo "   ⚠️"
            echo "   ⚠️  Resolve by keeping exactly one source copy:"
            echo "   ⚠️    A) Keep docs/ version and remove others"
            echo "   ⚠️    B) Keep .agents/ version and remove others"
            echo "   ⚠️    C) Keep root version and remove others"
            echo "   ⚠️    D) Inspect diffs, merge manually, then keep one copy"
            echo "   ⚠️  ─────────────────────────────────────────────────────"
            COLLISION_FOUND=true
        else
            source="${SPEC_MAP[$name]}"
            dest="$AGY_WORKFLOWS/$name"
            # Skip if source IS already the workflows/ copy (no-op / loop prevention)
            source_real=$(realpath "$source" 2>/dev/null || echo "$source")
            dest_real=$(realpath "$dest" 2>/dev/null || echo "$dest")
            if [ "$source_real" = "$dest_real" ]; then
                echo "   ℹ️  $name: source is already in $AGY_WORKFLOWS/ — skipping self-copy."
            else
                cp "$source" "$dest"
                echo "   ✅ $AGY_WORKFLOWS/$name (from $source)"
                SYNCED_COUNT=$((SYNCED_COUNT + 1))
            fi
        fi
    done

    if [ "$COLLISION_FOUND" = true ]; then
        echo ""
        echo "   ❌ One or more AgentSpec collisions were skipped. Re-run after resolving."
    fi

    if [ "$SYNCED_COUNT" -gt 1 ]; then
        echo "   ℹ️  $SYNCED_COUNT AgentSpec files synced to workflows/."
        echo "      Multi-spec projects are supported. Antigravity loads all of them."
    fi
fi

# Copy skills to .agents/skills/ (each skill is its own folder)
if [ -d "$SKILLS_DIR" ]; then
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            mkdir -p "$AGY_SKILLS/$skill_name"
            cp -r "$skill_dir"* "$AGY_SKILLS/$skill_name/"
            echo "   ✅ $AGY_SKILLS/$skill_name/"
        fi
    done
else
    echo "   ⚠️  $SKILLS_DIR not found — skipping skill sync."
    echo "      Skills will be created via /new-skill command."
fi

echo ""

# ─────────────────────────────────────────────────
# STEP 3: Verify
# ─────────────────────────────────────────────────
echo "📊 Step 3: Verification"
echo "   Tool files:"
for target in "${TOOL_TARGETS[@]}"; do
    if [ -f "$target" ]; then
        echo "      ✅ $target ($(wc -c < "$target") bytes)"
    else
        echo "      ❌ $target MISSING"
    fi
done

echo "   Antigravity:"
if [ -d "$AGY_WORKFLOWS" ]; then
    wf_count=$(find "$AGY_WORKFLOWS" -name "*.md" | wc -l)
    echo "      ✅ $AGY_WORKFLOWS/ ($wf_count workflows)"
fi
if [ -d "$AGY_SKILLS" ]; then
    sk_count=$(find "$AGY_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "      ✅ $AGY_SKILLS/ ($sk_count skills)"
fi

echo ""
echo "====================================="
echo "✅ Sync complete."
echo ""
echo "📌 Reminders:"
echo "   • For Gemini Custom Instructions: manually paste agent.md content"
echo "   • Commit all synced files together"
echo "   • Notify the team of any kernel changes"
