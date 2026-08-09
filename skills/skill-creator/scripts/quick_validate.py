#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # 호출 계층 규약 (docs/skill-invocation-tiers.md)
    INVOCATION_TIERS = {'user-invoked', 'model-invoked'}
    metadata = frontmatter.get('metadata') or {}
    if not isinstance(metadata, dict):
        return False, "'metadata' must be a mapping"
    invocation = metadata.get('invocation')
    if invocation is None:
        return False, (
            "Missing 'metadata.invocation' in frontmatter. "
            f"Declare one of: {', '.join(sorted(INVOCATION_TIERS))}. "
            "See docs/skill-invocation-tiers.md"
        )
    if invocation not in INVOCATION_TIERS:
        return False, (
            f"Invalid 'metadata.invocation' value: {invocation!r}. "
            f"Must be one of: {', '.join(sorted(INVOCATION_TIERS))}"
        )

    # 본문 최상단 인용 블록은 훅이 없는 환경의 최종 방어선이므로 함께 강제한다.
    # frontmatter 는 model 인데 본문은 user 인 불일치가 가장 위험한 조용한 실패다.
    body = content[match.end():]
    declared = re.search(r'^>\s*\*\*호출 계층:\s*([a-z-]+)\*\*', body, re.MULTILINE)
    if not declared:
        return False, (
            "Missing invocation tier callout at the top of the body. "
            f"Add: > **호출 계층: {invocation}** — ... "
            "See docs/skill-invocation-tiers.md"
        )
    if declared.group(1) != invocation:
        return False, (
            f"Invocation tier mismatch: frontmatter says {invocation!r} "
            f"but body callout says {declared.group(1)!r}"
        )

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (hyphen-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)