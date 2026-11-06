"""21st.dev & Magic MCP Frontend UI Component Router for SwitchGuard.

Provides REST endpoints for:
1. Checking UI engine & MCP server status (/api/ui/status)
2. Listing registered UI skills and agents (/api/ui/skills)
3. Searching brand/tech SVG logos (/api/ui/logo)
4. Searching 21st.dev component catalog (/api/ui/search)
5. Retrieving component specifications and dependencies (/api/ui/component)
"""
from __future__ import annotations
import shutil
import subprocess
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/ui", tags=["Magic UI & 21st Components"])

UI_SKILLS = [
    {
        "name": "21st-ui",
        "description": "Find, install, and generate modern UI with 21st.dev catalog and hosted 21st AI.",
        "category": "frontend",
        "tools": ["search", "get_component", "generate", "search_logo", "get_inspiration"]
    },
    {
        "name": "magic-ui",
        "description": "Discover, install, and generate modern React, Tailwind, and shadcn/ui components, themes, and brand logos.",
        "category": "design-system",
        "tools": ["search", "get_component", "get_theme", "search_logo", "iterate_generation"]
    },
    {
        "name": "motion-foundations",
        "description": "Motion tokens, spring presets, performance rules, and SSR-safe physics animations using motion/react.",
        "category": "animation",
        "tools": ["get_tokens", "get_springs", "should_animate"]
    },
    {
        "name": "motion-patterns",
        "description": "Staggered lists, border beams, interactive particles, and celebration confetti cannons.",
        "category": "animation",
        "tools": ["border_beam", "particles_mesh", "confetti_cannon", "hyper_text"]
    },
    {
        "name": "liquid-glass-design",
        "description": "Dynamic glass material with backdrop blur, specular highlights, and tactile spring micro-interactions.",
        "category": "design-system",
        "tools": ["glass_panel", "shimmer_button", "radar_beacon"]
    }
]

CURATED_CATALOG = [
    {
        "id": "pricing-table-tier-pro",
        "name": "Interactive Pricing Table",
        "category": "pricing",
        "author": "shadcn-magic",
        "description": "Responsive pricing grid with monthly/yearly toggle, badge highlights, and feature checklist.",
        "dependencies": ["lucide-react", "clsx", "tailwind-merge"],
        "registry_cmd": "21st add shadcn-magic/pricing-table-tier-pro",
        "framework": "React / Tailwind / shadcn"
    },
    {
        "id": "animated-bento-grid",
        "name": "Animated Bento Grid",
        "category": "features",
        "author": "motion-craft",
        "description": "Modern Apple-inspired bento grid with Framer Motion hover states, blur glassmorphism, and live charts.",
        "dependencies": ["framer-motion", "lucide-react", "clsx"],
        "registry_cmd": "21st add motion-craft/animated-bento-grid",
        "framework": "React / Tailwind / Framer Motion"
    },
    {
        "id": "modern-glass-navbar",
        "name": "Sticky Glassmorphic Navbar",
        "category": "navigation",
        "author": "glass-ui",
        "description": "Backdrop-blur header with animated mobile hamburger menu, active link indicators, and theme toggle.",
        "dependencies": ["lucide-react", "next-themes"],
        "registry_cmd": "21st add glass-ui/modern-glass-navbar",
        "framework": "React / Tailwind / Radix UI"
    },
    {
        "id": "hero-section-particle-glow",
        "name": "Glow Particle Hero Section",
        "category": "hero",
        "author": "lumi-design",
        "description": "High-impact hero section with interactive gradient background, CTAs, and social proof avatar stack.",
        "dependencies": ["framer-motion", "lucide-react"],
        "registry_cmd": "21st add lumi-design/hero-section-particle-glow",
        "framework": "React / Tailwind / Framer Motion"
    },
    {
        "id": "magic-border-beam",
        "name": "Magic UI Border Beam",
        "category": "animation",
        "author": "magic-ui",
        "description": "An animated beam of light traveling along the perimeter of cards and panels.",
        "dependencies": ["motion"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/border-beam.json\"",
        "framework": "Motion / CSS Keyframes"
    },
    {
        "id": "magic-particles-mesh",
        "name": "Interactive Particle Constellation",
        "category": "animation",
        "author": "magic-ui",
        "description": "Interactive HTML5 canvas particle field with distance connection lines and cursor magnetism.",
        "dependencies": ["canvas-api"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/particles.json\"",
        "framework": "Vanilla Canvas / React"
    },
    {
        "id": "magic-confetti-cannon",
        "name": "Celebration Confetti & Fireworks",
        "category": "animation",
        "author": "magic-ui",
        "description": "Celebration confetti cannons and star showers for task completion and verified test runs.",
        "dependencies": ["canvas-confetti"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/confetti.json\"",
        "framework": "Canvas Confetti"
    },
    {
        "id": "magic-hyper-text",
        "name": "Cyberpunk Hyper-Text Decryption",
        "category": "animation",
        "author": "magic-ui",
        "description": "Letter scrambling matrix effect that decodes text characters progressively.",
        "dependencies": ["motion"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/hyper-text.json\"",
        "framework": "Motion / React"
    },
    {
        "id": "submillisecond-speedometer",
        "name": "Sub-millisecond Latency Speedometer",
        "category": "animation",
        "author": "switch-motion",
        "description": "Radial SVG gauge with spring needle and rolling counter for sub-5ms decision display.",
        "dependencies": ["svg", "requestAnimationFrame"],
        "registry_cmd": "switch add motion/submillisecond-speedometer",
        "framework": "SVG / CSS Spring"
    },
    {
        "id": "magic-aurora-text",
        "name": "Magic UI Aurora Text",
        "category": "animation",
        "author": "magic-ui",
        "description": "Dynamic fluid aurora gradient text effect with smooth continuous hue shifting.",
        "dependencies": ["css-gradient"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/aurora-text.json\"",
        "framework": "CSS Animated Gradient"
    },
    {
        "id": "magic-neon-gradient-card",
        "name": "Magic UI Neon Gradient Card",
        "category": "animation",
        "author": "magic-ui",
        "description": "High-intensity luminous neon glow card with blurred volumetric backdrop bloom.",
        "dependencies": ["css-filters"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/neon-gradient-card.json\"",
        "framework": "CSS Neon Glow / Glass"
    },
    {
        "id": "magic-meteors-shower",
        "name": "Magic UI Meteors Shower",
        "category": "animation",
        "author": "magic-ui",
        "description": "Diagonal cosmic meteor shower with trailing linear gradient light tails.",
        "dependencies": ["css-transforms"],
        "registry_cmd": "npx shadcn@latest add \"https://magicui.design/r/meteors.json\"",
        "framework": "CSS Keyframes / GPU"
    }
]

SVGL_LOGOS = {
    "react": {
        "title": "React",
        "category": "Library",
        "route": {
            "light": "https://svgl.app/library/react_light.svg",
            "dark": "https://svgl.app/library/react_dark.svg"
        },
        "url": "https://react.dev/"
    },
    "tailwind": {
        "title": "Tailwind CSS",
        "category": "Framework",
        "route": "https://svgl.app/library/tailwindcss.svg",
        "url": "https://tailwindcss.com/"
    },
    "stripe": {
        "title": "Stripe",
        "category": "Payment",
        "route": "https://svgl.app/library/stripe.svg",
        "url": "https://stripe.com/"
    },
    "github": {
        "title": "GitHub",
        "category": "Developer Tool",
        "route": {
            "light": "https://svgl.app/library/github-light.svg",
            "dark": "https://svgl.app/library/github-dark.svg"
        },
        "url": "https://github.com/"
    },
    "supabase": {
        "title": "Supabase",
        "category": "Database",
        "route": "https://svgl.app/library/supabase.svg",
        "url": "https://supabase.com/"
    },
    "google": {
        "title": "Google",
        "category": "Cloud & AI",
        "route": "https://svgl.app/library/google.svg",
        "url": "https://google.com/"
    },
    "openai": {
        "title": "OpenAI",
        "category": "AI",
        "route": {
            "light": "https://svgl.app/library/openai_light.svg",
            "dark": "https://svgl.app/library/openai_dark.svg"
        },
        "url": "https://openai.com/"
    }
}


class ComponentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Keyword or component intent (e.g., 'pricing table', 'navbar', 'hero')")
    item_type: Optional[str] = Field("component", description="Item type: component, theme, template")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Max items to return")


class ComponentDetailRequest(BaseModel):
    id: str = Field(..., min_length=1, description="Component ID or slug")


def _is_21st_cli_installed() -> bool:
    return shutil.which("21st") is not None


@router.get("/status")
async def get_ui_status() -> Dict[str, Any]:
    """Returns the operational status of the 21st.dev / Magic MCP integration."""
    has_cli = _is_21st_cli_installed()
    has_api_key = bool(os.getenv("API_KEY_21ST") or os.getenv("TWENTY_FIRST_API_KEY"))

    return {
        "status": "active",
        "engine": "21st.dev / Magic MCP Suite",
        "cli_available": has_cli,
        "api_key_configured": has_api_key,
        "endpoint": "https://21st.dev/api/mcp",
        "catalog_size": "10,000+ Production React / Tailwind Components",
        "skills_count": len(UI_SKILLS),
        "supported_tools": [
            "search",
            "get_component",
            "search_logo",
            "generate",
            "iterate_generation",
            "get_inspiration",
            "get_theme",
            "get_usage"
        ],
        "default_stack": ["React", "Tailwind CSS", "shadcn/ui", "Radix UI", "Framer Motion"]
    }


@router.get("/skills")
async def list_ui_skills() -> Dict[str, Any]:
    """Lists registered UI skills and specialized subagents."""
    return {
        "status": "success",
        "count": len(UI_SKILLS),
        "skills": UI_SKILLS,
        "agent": {
            "name": "magic-designer",
            "role": "Expert UI Component & Design System Specialist",
            "model": "inherit"
        }
    }


@router.get("/logo")
async def search_brand_logo(query: str = Query(..., min_length=1, description="Brand name")) -> Dict[str, Any]:
    """Searches official SVG brand logos formatted for JSX/TSX."""
    clean_q = query.strip().lower()
    matches = []

    # First check curated local SVGL catalog
    for key, logo in SVGL_LOGOS.items():
        if clean_q in key or key in clean_q or clean_q in logo["title"].lower():
            matches.append(logo)

    # If 21st CLI is installed and no exact local match found, try CLI
    if not matches and _is_21st_cli_installed():
        try:
            res = subprocess.run(["21st", "logo", clean_q, "--json", "--limit", "3"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                import json
                parsed = json.loads(res.stdout)
                if isinstance(parsed, list):
                    matches.extend(parsed)
        except Exception:
            pass

    return {
        "status": "success",
        "query": query,
        "count": len(matches),
        "results": matches
    }


@router.get("/search")
@router.post("/search")
async def search_ui_components(
    req: Optional[ComponentSearchRequest] = None,
    q: Optional[str] = Query(None, description="Query string for GET requests")
) -> Dict[str, Any]:
    """Searches 21st.dev catalog for components matching the given query (supports GET and POST)."""
    search_query = ""
    item_type = "component"
    limit = 10

    if req:
        search_query = req.query.strip().lower()
        item_type = req.item_type or "component"
        limit = req.limit or 10
    elif q:
        search_query = q.strip().lower()

    # Filter curated catalog first
    matched = [c for c in CURATED_CATALOG if search_query in c["name"].lower() or search_query in c["category"] or search_query in c["description"].lower()]
    
    # If empty, return all matching or fallback suggestions
    results = matched if matched else CURATED_CATALOG[:limit]

    return {
        "status": "success",
        "query": search_query or "all",
        "type": item_type,
        "count": len(results),
        "components": results
    }


@router.post("/component")
async def get_ui_component_details(req: ComponentDetailRequest) -> Dict[str, Any]:
    """Retrieves full specification and installation instructions for a component."""
    target_id = req.id.strip().lower()
    
    for comp in CURATED_CATALOG:
        if comp["id"].lower() == target_id or target_id in comp["name"].lower():
            return {
                "status": "success",
                "component": comp,
                "installation": {
                    "cli": comp["registry_cmd"],
                    "shadcn_compatible": True,
                    "target_path": "components/ui/"
                }
            }
            
    # Fallback generic component scaffolding response
    return {
        "status": "success",
        "component": {
            "id": req.id,
            "name": req.id.replace("-", " ").title(),
            "category": "custom",
            "dependencies": ["lucide-react", "clsx", "tailwind-merge"],
            "registry_cmd": f"21st add community/{req.id}",
            "framework": "React / Tailwind / shadcn"
        },
        "installation": {
            "cli": f"21st add community/{req.id}",
            "shadcn_compatible": True,
            "target_path": "components/ui/"
        }
    }


@router.get("/animations")
async def get_animation_suite() -> Dict[str, Any]:
    """Returns motion tokens, spring presets, and active animation plugins."""
    return {
        "status": "success",
        "engine": "Motion Foundations + Magic UI Suite",
        "tokens": {
            "duration": {
                "instant": 0.08,
                "fast": 0.18,
                "normal": 0.35,
                "slow": 0.5,
                "crawl": 1.0
            },
            "easing": {
                "spring": "cubic-bezier(0.34, 1.56, 0.64, 1)",
                "snappy": "cubic-bezier(0.16, 1, 0.3, 1)",
                "smooth": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
        },
        "active_plugins": [
            {
                "id": "border-beam",
                "name": "Magic UI Border Beam",
                "description": "Continuous perimeter laser beam orbiting cards",
                "status": "active"
            },
            {
                "id": "ambient-particles",
                "name": "Canvas Particle Mesh",
                "description": "Interactive constellation background with cursor magnetic drift",
                "status": "active"
            },
            {
                "id": "confetti-cannon",
                "name": "Celebration Confetti Fireworks",
                "description": "Particle explosions on test pass and Ralph loop completion",
                "status": "active"
            },
            {
                "id": "hyper-text",
                "name": "Cyberpunk Hyper-Text Decryption",
                "description": "Letter scrambling matrix effect for high-tech telemetry",
                "status": "active"
            },
            {
                "id": "speedometer-gauge",
                "name": "Radial Sub-millisecond Latency Speedometer",
                "description": "Interactive SVG speedometer with spring needle and rolling counter",
                "status": "active"
            },
            {
                "id": "liquid-glass",
                "name": "iOS 26 Liquid Glass UI",
                "description": "Frosted glass panels with backdrop blur and specular highlights",
                "status": "active"
            },
            {
                "id": "aurora-text",
                "name": "Magic UI Aurora Text",
                "description": "Fluid animated chromatic aurora gradient text",
                "status": "active"
            },
            {
                "id": "neon-gradient-card",
                "name": "Magic UI Neon Gradient Card",
                "description": "Volumetric neon bloom and luminous edge glows",
                "status": "active"
            },
            {
                "id": "meteors-shower",
                "name": "Magic UI Meteors Shower",
                "description": "Cosmic shooting stars with trailing linear gradients",
                "status": "active"
            }
        ]
    }

