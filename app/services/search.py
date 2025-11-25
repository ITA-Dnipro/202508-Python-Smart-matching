import httpx
import os
import asyncio
import numpy as np
from .embeddings import embed_text
from ..api.schema import MatchResult
from ..core.exceptions import UserNotFoundException, MonolithServiceException
from ..core.state import app_state
from .vector_db import search_similar_startups

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
if not USER_SERVICE_URL:
    raise EnvironmentError("USER_SERVICE_URL is not set in .env")


async def fetch_investor_profile_text(investor_id: int, authorization: str) -> str:
    """
        Fetches an investor's text profile (industry name) from the monolith API.
    """
    headers = {"Authorization": authorization}
    url_profile = f"{USER_SERVICE_URL}/api/profiles/investor-profiles/{investor_id}/"
    investment_focus_id = None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:

            response_profile = await client.get(url_profile, headers=headers)
            response_profile.raise_for_status()

            profile_data = response_profile.json()
            investment_focus_id = profile_data.get("investment_focus")

            if investment_focus_id is None:
                raise MonolithServiceException(f"Investor {investor_id} found, but has no 'investment_focus' ID.")

            url_industry = f"{USER_SERVICE_URL}/api/profiles/industries/{investment_focus_id}/"
            response_industry = await client.get(url_industry, headers=headers)
            response_industry.raise_for_status()

            industry_data = response_industry.json()

            focus_text = industry_data.get("industry_name")

            if not focus_text:
                raise MonolithServiceException(f"Industry {investment_focus_id} found, but has no 'name' field.")

            return focus_text

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            if str(e.request.url) == url_profile:
                raise UserNotFoundException(f"Investor with id {investor_id} not found.")
            else:
                raise MonolithServiceException(f"Industry with id {investment_focus_id} not found in monolith.")
        if e.response.status_code == 401:
            raise MonolithServiceException("Authorization failed for monolith.")

        raise MonolithServiceException(f"Monolith HTTP error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise MonolithServiceException(f"Cannot connect to User Service: {e.request.url}")


def perform_search_by_text(text: str, top_k: int) -> list[MatchResult]:
    query_vector = embed_text(text).tolist()
    return search_similar_startups(query_vector, top_k)


async def find_matches_for_investor(investor_id: int, top_k: int, authorization: str) -> list[MatchResult]:
    """
        Orchestrates the search: fetches investor text and finds matching startups.
    """
    investor_focus_text = await fetch_investor_profile_text(investor_id = investor_id,
                                                      authorization=authorization)

    results = perform_search_by_text(
        text=investor_focus_text,
        top_k=top_k
    )

    return results