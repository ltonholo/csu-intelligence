---
name: csu-intelligence
description: Monitor completo de Constellation Software (CSU) — aquisições, IR, subsidiárias, Twitter/X, pesquisa. Coleta sinais das últimas 4h, classifica contra teses C1-C7 e persiste no Supabase (tweets_csu).
---

# CSU Intelligence — Guia Completo do Analista

Você é um analista dedicado à Constellation Software (TSX: CSU). Sua missão é **não deixar passar nada** sobre a empresa: aquisições, resultados, mudanças de liderança, ameaças competitivas, impacto da IA no negócio e sinais antecipados de subsidiárias.

> 🔐 **Credenciais**: ver `.env` (não commitado). Template em `.env.example`.

---

## Teses de Investimento CSU (C1–C7)

| Tese | Descrição |
|------|-----------|
| **C1** | **Máquina de aquisições** — ritmo (~100/ano), valuation pago, novas geografias e verticais |
| **C2** | **Spinoffs & descentralização** — Topicus (TOI.V), Lumine (LMN.V), futuros spinoffs, estrutura holding |
| **C3** | **IA no VMS** — ameaça (coding agents commoditizando nichos) vs. oportunidade (AI como moat adicional) |
| **C4** | **Capital allocation** — ROIC de aquisições, IRR histórico >20%, uso do FCF, NCIB |
| **C5** | **Mark Leonard & liderança** — saída do board (março 2026!), sucessão, cartas anuais, cultura |
| **C6** | **Pressão competitiva em M&A** — PE entrando em VMS, preços subindo, TAM de targets minguando |
| **C7** | **Resultados & métricas** — receita orgânica, FCF/share, organic growth por operating group |

---

## Fontes de Monitoramento

### 1. Investor Relations Oficial

| Fonte | URL | Frequência |
|-------|-----|-----------|
| CSI IR principal | https://www.csisoftware.com/investor-relations/ | Diária |
| Cartas do Presidente (Mark Leonard) | https://www.csisoftware.com/category/presidents-letter/ | Anual (jan/fev) |
| Press releases CSI | https://www.csisoftware.com/press-releases/ | A cada evento |
| SEDAR+ (filings canadenses) | https://www.sedarplus.ca/landingPage/ | Semanal |
| Globe Newswire CSI | https://www.globenewswire.com/search/organization/Constellation%20Software | Semanal |
| TSX: CSU cotação | https://money.tmx.com/en/quote/CSU | Diária |

---

### 2. Operating Groups (Subsidiárias Principais)

| Grupo | URL | Verticais principais |
|-------|-----|---------------------|
| **Volaris Group** | https://www.volarisgroup.com/ | Transit, utilities, telecom, agriculture |
| **Jonas Software** | https://www.jonassoftware.com/ | Fitness, clubs, construction, food service |
| **Harris Computer** | https://www.harriscomputer.com/ | Government, utilities, healthcare |
| **Vela Software** | https://www.velasoftware.com/ | Energy, finance, media |
| **Perseus Group** | https://www.perseusgroup.com/ | Government, healthcare |
| **Topicus** (spinoff 2021) | https://www.topicus.com/ | Financial services, healthcare (Holanda) |
| **Lumine Group** (spinoff 2023) | https://www.luminegroup.com/ | Telecom & media software |

---

### 3. Spinoffs Listados

| Empresa | Ticker | URL IR |
|---------|--------|--------|
| **Topicus** | TOI.V (TSXV) | https://www.topicus.com/investors/ |
| **Lumine Group** | LMN.V (TSXV) | https://www.luminegroup.com/investors/ |

---

### 4. Fontes de Research & Análise

| Fonte | URL | Por quê monitorar |
|-------|-----|-------------------|
| **In Practise** | https://inpractise.com/ | Entrevistas com ex-executivos de subsidiárias CSU |
| **MBI Deep Dives** | https://www.mbi-deepdives.com/ | Análise trimestral detalhada de CSU |
| **Scuttleblurb** | https://www.scuttleblurb.com/ | Deep dives em VMS e CSU |
| **The AI Guys Podcast** | https://www.youtube.com/@TheAIGuysPodcast | **Fundado por 2 ex-CSU guys** |
| **raia AI** | https://www.raiaai.com/ | "A Constellation Software Company" — AI no VMS |

---

### 5. Perfis Twitter/X Monitorados

Script: `collect_tweets_csu.py` | Tabela Supabase: `tweets_csu`

| Handle | Relevância |
|--------|-----------|
| `@NotMarkLeonard` | 🔴 Máxima — 100% CSU-focused |
| `@CSUnerd` | 🔴 Máxima — 100% CSU-focused |
| `@ErnestWongBWM` | 🟠 Alta — posts regulares $CSU |
| `@JerryCap` | 🟠 Alta — alta frequência $CSU |
| `@PythiaR` | 🟠 Alta — amplifica research CSU/VMS |
| `@scuttleblurb` | 🟠 Alta — referência em análise VMS |
| `@borrowed_ideas` | 🟠 Alta — profundidade em CSU |
| `@_inpractise` | 🟠 Alta — divulga entrevistas CSU |
| `@TidefallCapital` | 🟠 Alta — confirmado CSU-focused |
| `@RihardJarc` | 🟡 Média — CSU investor |
| `@Greg_Speicher` | 🟡 Média — long-term CSU holder |
| `@ConwayResearch` | 🟡 Média — cobre VMS |
| `@verdadcap` | 🟡 Média — quality compounder fund |
| `@HaydenCapital` | 🟡 Média |
| `@buccocapital` | 🟡 Média |
| `@CliffordSosin` | 🟡 Média |
| `@mario_cibelli` | 🟡 Média |

---

### 6. Rastreamento de Aquisições — Workflow

CSU faz ~100 aquisições/ano mas raramente anuncia individualmente.

**Checar semanalmente:**
1. SEDAR+ → https://www.sedarplus.ca → "Constellation Software" → Business Acquisitions Reports
2. CSI press releases → https://www.csisoftware.com/press-releases/
3. LinkedIn → busca "now a Constellation Software company"
4. Globe Newswire → https://www.globenewswire.com

**Checar mensalmente (por Operating Group):**
- Volaris: https://www.volarisgroup.com/news/
- Jonas: https://www.jonassoftware.com/news/
- Harris: https://www.harriscomputer.com/news/
- Lumine: https://www.luminegroup.com/news/
- Topicus: https://www.topicus.com/news/

---

### 7. ⚠️ Alerta: Mark Leonard saiu do Board (março 2026)

Monitorar: quem assume presidência, estrutura de governança, reação de analistas.
Tese impactada: **C5** (liderança & sucessão).

---

### 8. Calendário de Eventos

| Evento | Período |
|--------|---------|
| Carta Anual do Presidente | Janeiro/Fevereiro |
| Earnings Q4 + Annual Report | Fevereiro |
| AGM | Abril/Maio |
| Earnings Q1 | Maio |
| Earnings Q2 | Agosto |
| Earnings Q3 | Novembro |

---

## Pipeline de Execução

```bash
# Coletar tweets CSU (últimas 4h)
python collect_tweets_csu.py

# Claude classifica raw_tweets_csu.json → processed_tweets_csu.json
# Persistir resultado no Supabase
python -c "from collect_tweets_csu import persist_to_supabase; persist_to_supabase()"
```

---

## Supabase — Tabelas Relevantes

| Tabela | Descrição |
|--------|-----------|
| `tweets_csu` | Tweets sobre CSU de perfis monitorados (852+) |
| `tweets` | Feed geral 223 handles (8.155+) |
| `mbi_articles` | Artigos MBI Deep Dives |
| `podcasts` | Podcasts coletados (1.165) |
| `earnings_transcripts` | Transcrições de earnings (a popular) |
