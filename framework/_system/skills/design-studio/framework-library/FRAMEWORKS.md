# Framework Library — the best, by GitHub stars (researched 2026-06-05)

> Live star counts pulled from the GitHub API on 2026-06-05. Stars move; re-pull periodically with
> the script in §Refresh. This is the **tooling layer** of the design system:
>
> **STRUCTURE** (`layout-library/ARCHETYPES.md`) × **STYLE** (`awesome-design-library/*.md` brand DNA) × **TOOLING** (this file)
>
> Rule: don't reach for the same stack every time any more than the same layout. Pick the tool that
> fits the job, and vary across the portfolio. Every entry has a **grab** command — copy-paste ready.

---

## ★ Recommended default for the user's client sites
**Marketing / local-business sites (most jobs):** **Astro + Tailwind + a component kit (shadcn/ui or daisyUI) + Motion or GSAP for the wow.** Astro ships ~zero JS, scores top Core Web Vitals (which we sell), and renders fast content sites. Reach for **Next.js** instead only when the site needs heavy interactivity (the live-AI-demo, dashboards, auth).
- Variety lever: rotate the component kit + animation lib per client so two sites never feel identical.

---

## 1. Frameworks & meta-frameworks (the foundation)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 245.6k | **React** | UI library; base of most kits | `npm create vite@latest my-site -- --template react-ts` |
| 139.9k | **Next.js** | React meta-framework — interactive sites, apps, the AI demo | `npx create-next-app@latest` |
| 100.3k | **Angular** | Enterprise SPA framework | `npm i -g @angular/cli && ng new` |
| 86.9k | **Svelte / SvelteKit** | Compiler-based, lean, delightful DX | `npx sv create` |
| 60.4k | **Nuxt** | Vue meta-framework | `npm create nuxt@latest` |
| 59.9k | **Astro** ⭐ | Content/marketing sites, islands, ~0 JS, best CWV | `npm create astro@latest` |
| 56.0k | **Gatsby** | React SSG (older, data-layer heavy) | `npm init gatsby` |
| 53.8k | **Vue 3** | Progressive framework | `npm create vue@latest` |
| 38.7k | **Preact** | 3kB React-compatible alt | `npm create preact@latest` |
| 35.6k | **SolidJS** | Fine-grained reactivity, very fast | `npx degit solidjs/templates/ts my-app` |
| 33.0k | **Remix / React Router** | Web-standards React, great forms/data | `npx create-react-router@latest` |
| 27.2k | **Quasar** | Vue app framework (web+mobile+desktop) | `npm i -g @quasar/cli && quasar create` |
| 22.0k | **Qwik** | Resumability, instant load | `npm create qwik@latest` |
| 18.7k | **Framework7** | iOS/Android-styled HTML app framework | `npx create-framework7-app` |

## 2. Static-site generators (content & blogs)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 88.4k | **Hugo** ⭐ | World's fastest SSG (Go) — blogs/content at scale | `hugo new site mysite` |
| 65.1k | **Docusaurus** | Docs / knowledge sites | `npx create-docusaurus@latest` |
| 51.5k | **Jekyll** | Ruby SSG, native GitHub Pages | `jekyll new mysite` |
| 19.7k | **Eleventy (11ty)** ⭐ | Simple, flexible JS SSG — hand-crafted bespoke sites | `npm i @11ty/eleventy` |

## 3. CSS frameworks & engines (the styling base)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 174.3k | **Bootstrap** | Classic component CSS framework, fast & familiar | `npm i bootstrap` |
| 95.4k | **Tailwind CSS** ⭐ | Utility-first, the modern standard | `npm i tailwindcss @tailwindcss/vite` |
| 50.1k | **Bulma** | Clean Flexbox class-based CSS | `npm i bulma` |
| 18.8k | **UnoCSS** | Instant on-demand atomic CSS (Tailwind-like, faster) | `npm i -D unocss` |
| 16.6k | **Pico CSS** ⭐ | Classless semantic CSS — gorgeous fast simple sites | `npm i @picocss/pico` |
| 5.4k | **Open Props** | CSS-variable design tokens (great for hand-rolled) | `npm i open-props` |

## 4. UI component libraries (the look, fast)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 115.8k | **shadcn/ui** ⭐ | Copy-paste Radix+Tailwind, code you OWN — modern default | `npx shadcn@latest init` |
| 98.4k | **MUI (Material UI)** | Comprehensive React Material components | `npm i @mui/material` |
| 98.3k | **Ant Design** | Enterprise React UI | `npm i antd` |
| 41.1k | **daisyUI** ⭐ | Tailwind component classes — fastest theming | `npm i -D daisyui` |
| 40.4k | **Chakra UI** | Accessible React component system | `npm i @chakra-ui/react` |
| 31.2k | **Mantine** | Full-featured React components + hooks | `npm i @mantine/core @mantine/hooks` |
| 29.6k | **HeroUI** (ex-NextUI) | Beautiful modern React UI | `npm i @heroui/react` |
| 28.6k | **Headless UI** | Unstyled accessible primitives (Tailwind team) | `npm i @headlessui/react` |
| 27.5k | **Element Plus** | Vue 3 UI library | `npm i element-plus` |
| 22.6k | **React-Bootstrap** | Bootstrap as React components | `npm i react-bootstrap` |
| 18.9k | **Radix Primitives** | Headless accessible primitives (shadcn's base) | `npm i radix-ui` |
| 14.4k | **PrimeVue** | Vue UI suite | `npm i primevue` |
| 9.3k | **Flowbite** | Tailwind component library | `npm i flowbite` |
| 8.4k | **Radix Themes** | Pre-styled Radix component library | `npm i @radix-ui/themes` |
| 6.6k | **Nuxt UI** | Vue/Nuxt UI (Reka UI + Tailwind) | `npm i @nuxt/ui` |
| 3.5k | **Tremor** | React dashboard/chart components | `npm i @tremor/react` |

## 5. Animation, 3D & interaction (the wow)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 112.9k | **Three.js** | 3D in the browser | `npm i three` |
| 82.6k | **animate.css** | Drop-in CSS animations | `npm i animate.css` |
| 69.4k | **anime.js** | Lightweight JS animation engine | `npm i animejs` |
| 32.2k | **Motion** (Framer Motion) ⭐ | The React/JS animation standard | `npm i motion` |
| 31.6k | **Alpine.js** ⭐ | Minimal JS behavior in markup — "sprinkles," no framework | `npm i alpinejs` |
| 31.0k | **React Three Fiber** | React renderer for Three.js | `npm i @react-three/fiber three` |
| 25.6k | **GSAP** ⭐ | Pro-grade JS animation (now fully free) | `npm i gsap` |

## 6. Headless CMS (so clients edit their own content)
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 72.3k | **Strapi** | Leading open-source headless CMS | `npx create-strapi-app@latest` |
| 42.8k | **Payload** ⭐ | Next.js-native fullstack CMS | `npx create-payload-app` |
| 36.0k | **Directus** | DB → instant API + admin | `npx create-directus-project` |
| 9.9k | **Keystone** | GraphQL headless CMS (Node) | `npx create-keystone-app` |
| — | *Sanity* (SaaS, not OSS-starred) | Best editor DX for marketing sites | `npm create sanity@latest` |

## 7. Web builders, icons & utilities
| Stars | Tool | What / when | Grab |
|---|---|---|---|
| 58.2k | **Zustand** | Tiny React state | `npm i zustand` |
| 49.6k | **TanStack Query** | Async/server state | `npm i @tanstack/react-query` |
| 25.9k | **GrapesJS** | Open-source drag-drop web builder framework | `npm i grapesjs` |
| 23.6k | **Heroicons** | Icon set (Tailwind team) | `npm i @heroicons/react` |
| 22.9k | **Lucide** ⭐ | Beautiful consistent icon toolkit | `npm i lucide-react` |
| 8.0k | **Bootstrap Icons** | SVG icon library | `npm i bootstrap-icons` |

## 8. Starter / landing templates (clone-and-go)
| Stars | Repo | Grab |
|---|---|---|
| 4.5k | cruip/tailwind-landing-page-template | `git clone https://github.com/cruip/tailwind-landing-page-template` |
| — | Astro themes (hundreds, many free) | browse `astro.build/themes` |
| — | Vercel templates | browse `vercel.com/templates` |
| — | shadcn examples / blocks | `npx shadcn@latest add` |

---

## Refresh (re-pull stars later)
```bash
for r in withastro/astro vercel/next.js tailwindlabs/tailwindcss shadcn-ui/ui saadeghi/daisyui motiondivision/motion greensock/GSAP gohugoio/hugo 11ty/eleventy; do
  gh api "repos/$r" --jq '[.stargazers_count,.full_name]|@tsv'; done | sort -rn
```

## How this kills the "every site looks the same" problem
A site is three independent choices: **archetype** (bones) + **brand DNA** (skin) + **stack** (tools).
Rotate each. The user's v3 was Split-Marquee + example-heritage + hand-rolled CSS — fine once, stale twice.
Next build: a *different* archetype, the *same* brand DNA (it's the same brand), and pick a *fitting* stack
from above (e.g., Astro + Tailwind + daisyUI + GSAP). Three knobs, never all in the same position twice.
