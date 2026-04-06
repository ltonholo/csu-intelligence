"""
CSU X Intelligence — Coletor de Tweets sobre Constellation Software
Adaptado do pipeline x-feed-intelligence-report para focar exclusivamente em CSU.

Coleta tweets das últimas 4h dos perfis mais relevantes sobre Constellation Software,
classifica contra teses de investimento CSU-específicas e persiste no Supabase (tabela tweets_csu).

Pipeline: twitterapi.io → classificação LLM → Supabase (tweets_csu)
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
import time

# ── Configuração ────────────────────────────────────────────────────────────────

TWITTER_API_KEY   = "new1_a204535f76604a4c8be80fd86858206e"
TWITTER_BASE_URL  = "https://api.twitterapi.io"
FXTWITTER_BASE    = "https://api.fxtwitter.com"

SUPABASE_URL      = "https://cofshiuvruulafhqglvu.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNvZnNoaXV2cnV1bGFmaHFnbHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxMzMzNTYsImV4cCI6MjA5MDcwOTM1Nn0.hyBqp40WKnwsecDBH_S_MGfXxb8x-twiRHzovOCkD2s"
SUPABASE_TABLE    = "tweets_csu"

COLLECTION_HOURS  = 4   # Janela de coleta
OUTPUT_RAW        = "raw_tweets_csu.json"
OUTPUT_PROCESSED  = "processed_tweets_csu.json"

# ── Perfis monitorados ──────────────────────────────────────────────────────────
#
# Seleção criteriosa de handles focados em Constellation Software / VMS:
#
# 🏛️  Investidores & Analistas Core CSU
#   NotMarkLeonard  — conta que parodia/analisa Mark Leonard; 100% CSU-focused
#   CSUnerd         — analista dedicado a Constellation Software
#   ErnestWongBWM   — portfolio manager com cobertura regular de $CSU
#   JerryCap        — investidor com alta frequência de posts sobre CSU
#   PythiaR         — analista que amplifica research sobre CSU/VMS
#   scuttleblurb    — referência em análise profunda de VMS e CSU
#   borrowed_ideas  — gestor VMS-focused, cobre CSU com profundidade
#   RihardJarc      — investidor europeu focado em CSU
#   Greg_Speicher   — value investor, long-term CSU holder
#   ConwayResearch  — research house que cobre VMS
#   verdadcap       — fundo focado em quality compounders, inclui CSU
#   cckeleti        — analista CSU/VMS no Twitter
#   HaydenCapital   — gestor que inclui CSU no portfolio
#   buccocapital    — gestor com foco em quality compounder
#   CliffordSosin   — gestor value, CSU holder
#   mario_cibelli   — value investor com cobertura CSU
#   AndrewRangeley  — analista sell-side que cobre CSU área
#
# 📚  Research & Deep Dives
#   _inpractise     — In Practise: entrevistas com ex-executivos de subsidiárias CSU
#   TidefallCapital — fundo confirmado CSU-focused (via tweet sobre The AI Guys)
#
# 🏢  Relacionados Institucionais
#   TheAIGuysPodcast (YouTube) — fundado por 2 ex-CSU guys (cofundadores offrs.com, adquirida CSU)

CSU_HANDLES = [
    # Core CSU investors & analysts
    "NotMarkLeonard",
    "CSUnerd",
    "ErnestWongBWM",
    "JerryCap",
    "PythiaR",
    "scuttleblurb",
    "borrowed_ideas",
    "RihardJarc",
    "Greg_Speicher",
    "ConwayResearch",
    "verdadcap",
    "cckeleti",
    "HaydenCapital",
    "buccocapital",
    "CliffordSosin",
    "mario_cibelli",
    "AndrewRangeley",
    # Research houses
    "_inpractise",
    "TidefallCapital",
]

# ── Teses de investimento CSU-específicas ───────────────────────────────────────
#
# Adaptação das teses gerais para o contexto da Constellation Software:
#
# C1: Máquina de aquisições — ritmo, valuations, novos geografias/verticais
# C2: Spinoffs & descentralização — Topicus, futuros spinoffs, estrutura holding
# C3: Impacto da IA no VMS — ameaça ou oportunidade para software vertical legado
# C4: Capital allocation — ROIC, IRR de aquisições, uso de caixa
# C5: Mark Leonard & liderança — saída do board, sucessão, cartas aos shareholders
# C6: Ambiente competitivo — PE vs CSU em acquisitions, preços subindo
# C7: Resultados e métricas — receita, FCF, organic growth, guidance

CSU_TESES = {
    "C1": "Máquina de aquisições — ritmo, valuations, novos geografias/verticais",
    "C2": "Spinoffs & descentralização — Topicus, futuras separações, estrutura",
    "C3": "Impacto da IA no VMS — ameaça ou oportunidade ao software vertical legado",
    "C4": "Capital allocation — ROIC, IRR de aquisições, uso do FCF",
    "C5": "Mark Leonard & liderança — saída do board, sucessão, cartas",
    "C6": "Ambiente competitivo — PE vs CSU em M&A, pressão de preços",
    "C7": "Resultados e métricas — receita, FCF, organic growth",
}

# ── Headers comuns ──────────────────────────────────────────────────────────────
TWITTER_HEADERS  = {"X-API-Key": TWITTER_API_KEY}
SUPABASE_HEADERS = {
    "apikey":        SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=ignore-duplicates",
}


# ── Etapa 1: Coletar tweets ─────────────────────────────────────────────────────

def get_user_id(handle: str) -> str | None:
    """Retorna o userId numérico de um handle via twitterapi.io."""
    url = f"{TWITTER_BASE_URL}/twitter/user/info"
    try:
        r = requests.get(url, headers=TWITTER_HEADERS,
                         params={"userName": handle}, timeout=15)
        r.raise_for_status()
        return r.json()["data"]["id"]
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar ID de @{handle}: {e}")
        return None


def get_timeline(user_id: str, count: int = 10) -> list:
    """Retorna tweets recentes do usuário (sem replies)."""
    url = f"{TWITTER_BASE_URL}/twitter/user/tweet_timeline"
    try:
        r = requests.get(url, headers=TWITTER_HEADERS,
                         params={"userId": user_id, "includeReplies": "false",
                                 "count": count}, timeout=15)
        r.raise_for_status()
        return r.json().get("data", {}).get("tweets", [])
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar timeline de {user_id}: {e}")
        return []


def get_thread_text(tweet_id: str) -> str | None:
    """Busca texto completo da thread via fxtwitter."""
    url = f"{FXTWITTER_BASE}/status/{tweet_id}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        thread = r.json().get("tweet", {}).get("thread", [])
        if thread:
            return "\n---\n".join(t.get("text", "") for t in thread)
    except Exception as e:
        print(f"  ⚠️  fxtwitter erro para {tweet_id}: {e}")
    return None


def collect_tweets() -> list:
    """Coleta tweets das últimas COLLECTION_HOURS horas de todos os CSU_HANDLES."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=COLLECTION_HOURS)
    raw_tweets = []

    for handle in CSU_HANDLES:
        print(f"📡 Coletando @{handle}...")
        user_id = get_user_id(handle)
        if not user_id:
            continue

        tweets = get_timeline(user_id)
        count = 0
        for tw in tweets:
            # Parsear data
            created_raw = tw.get("createdAt", "")
            try:
                created_dt = datetime.fromisoformat(
                    created_raw.replace("Z", "+00:00")
                )
            except ValueError:
                continue

            if created_dt < cutoff:
                continue  # Fora da janela de coleta

            tweet_id = tw.get("id") or tw.get("tweetId", "")
            conv_id  = tw.get("conversationId", "")
            is_thread = bool(conv_id and conv_id != tweet_id)

            # Buscar thread completa se necessário
            thread_text = None
            if is_thread:
                thread_text = get_thread_text(tweet_id)
                time.sleep(0.3)  # Respeitar rate limit fxtwitter

            raw_tweets.append({
                "id":          int(tweet_id) if tweet_id else None,
                "handle":      handle,
                "author":      tw.get("author", {}).get("name", handle),
                "text":        tw.get("text", ""),
                "thread_text": thread_text,
                "datetime":    created_dt.isoformat(),
                "url":         f"https://twitter.com/{handle}/status/{tweet_id}",
                "likes":       int(tw.get("likeCount", 0) or 0),
                "retweets":    int(tw.get("retweetCount", 0) or 0),
                "views":       int(tw.get("viewCount", 0) or 0),
                "is_thread":   is_thread,
            })
            count += 1

        print(f"  ✅ {count} tweets coletados")
        time.sleep(0.5)  # Rate limit entre handles

    print(f"\n📊 Total coletado: {len(raw_tweets)} tweets nas últimas {COLLECTION_HOURS}h")
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        json.dump(raw_tweets, f, ensure_ascii=False, indent=2)
    print(f"💾 Salvo em {OUTPUT_RAW}")
    return raw_tweets


# ── Etapa 2: Classificar tweets (executado pelo LLM / Claude) ───────────────────
#
# NOTA: Esta etapa é executada pelo Claude após collect_tweets().
# O LLM lê raw_tweets_csu.json e classifica cada tweet contra as teses C1-C7.
#
# Prompt sugerido para classificação:
#
# "Você é um analista especializado em Constellation Software (CSU).
#  Leia cada tweet abaixo e classifique:
#  - teses_relevantes: lista de C1-C7 (pode ser vazia)
#  - keywords: palavras-chave separadas por vírgula
#  - criticidade: CRITICA / ALTA / MEDIA / BAIXA
#  - resumo: 1 frase em PT resumindo o conteúdo (use thread_text se disponível)
#  - justificativa: por que essa criticidade
#
#  Para tweets com is_thread=true, use thread_text como fonte principal.
#  Foque em: aquisições, mark leonard, resultados, FCF, M&A, IA no VMS, spinoffs.
#  Salve em processed_tweets_csu.json."


# ── Etapa 3: Persistir no Supabase ─────────────────────────────────────────────

def persist_to_supabase(input_file: str = OUTPUT_PROCESSED) -> None:
    """Persiste tweets classificados na tabela tweets_csu do Supabase."""
    with open(input_file, encoding="utf-8") as f:
        tweets = json.load(f)

    rows = []
    for t in tweets:
        tweet_id = t.get("id")
        if not tweet_id:
            continue
        rows.append({
            "id":              int(tweet_id),
            "tweet_url":       t.get("url", ""),
            "handle":          t.get("handle", ""),
            "author":          t.get("author", ""),
            "text":            t.get("text", ""),
            "thread_text":     t.get("thread_text") or None,
            "tweet_datetime":  t.get("datetime") or None,
            "likes":           int(t.get("likes", 0) or 0),
            "retweets":        int(t.get("retweets", 0) or 0),
            "views":           int(t.get("views", 0) or 0),
            "is_thread":       bool(t.get("is_thread", False)),
            "teses_relevantes": t.get("teses_relevantes", []),
            "keywords":        t.get("keywords", ""),
            "criticidade":     t.get("criticidade", "BAIXA"),
            "resumo":          t.get("resumo", ""),
            "justificativa":   t.get("justificativa", ""),
            "collected_at":    datetime.utcnow().isoformat() + "Z",
        })

    inserted = 0
    for i in range(0, len(rows), 50):
        batch = rows[i : i + 50]
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=SUPABASE_HEADERS,
            json=batch,
            timeout=30,
        )
        if r.status_code in (200, 201):
            inserted += len(batch)
        else:
            print(f"  ⚠️  Erro batch {i}: {r.status_code} — {r.text[:200]}")

    print(f"\n✅ {inserted}/{len(rows)} tweets salvos em '{SUPABASE_TABLE}'")


# ── Etapa 4: Resumo da coleta ───────────────────────────────────────────────────

def print_summary(input_file: str = OUTPUT_RAW) -> None:
    """Imprime estatísticas rápidas da coleta."""
    with open(input_file, encoding="utf-8") as f:
        tweets = json.load(f)

    if not tweets:
        print("⚠️  Nenhum tweet coletado.")
        return

    by_handle = {}
    for t in tweets:
        by_handle[t["handle"]] = by_handle.get(t["handle"], 0) + 1

    print("\n📈 Resumo da coleta:")
    print(f"   Total de tweets: {len(tweets)}")
    print(f"   Threads:         {sum(1 for t in tweets if t['is_thread'])}")
    print("   Por handle:")
    for h, n in sorted(by_handle.items(), key=lambda x: -x[1]):
        print(f"     @{h}: {n}")


# ── Entry point ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🔭 CSU X Intelligence — Coletor de Tweets")
    print(f"   Janela: últimas {COLLECTION_HOURS}h")
    print(f"   Handles monitorados: {len(CSU_HANDLES)}")
    print("=" * 60)

    tweets = collect_tweets()
    print_summary(OUTPUT_RAW)

    print("\n⏳ Etapa 2 (classificação) deve ser executada pelo Claude.")
    print("   Após classificação, execute: persist_to_supabase()")
    print("\n   Ou para persistir diretamente sem classificação:")
    # persist_to_supabase(OUTPUT_RAW)  # Descomente para persistir sem classificação
