# TORRENTIO_URL = "https://torrentio.strem.fun"
# TORRENTIO_FILTERS = "qualityfilter=other,scr,cam"

# def scrape_show(imdbid: str = "tt0944947", season: int = 1, episode: int = 1) -> dict:
#     """Scrape a show from torrentio"""
#     url = f"{TORRENTIO_URL}/{TORRENTIO_FILTERS}/stream/series/{imdbid}:{season}:{episode}.json"
#     response = requests.get(url)
#     return response.json()

# def scrape_movie(imdbid: str = "tt0172495") -> dict:
#     """Scrape a movie from torrentio"""
#     url = f"{TORRENTIO_URL}/{TORRENTIO_FILTERS}/stream/movie/{imdbid}.json"
#     response = requests.get(url)
#     return response.json()

# def test_scrape_results_with_rank(settings_model, default_ranking) -> dict:
#     """Scrape a show from torrentio"""
#     results = {}
    
#     response: list = scrape_show().get("streams", [])
#     for result in response:
#         results[result["title"].split("\n")[0]] = result["infoHash"]
    
#     for k, v in results.items():
#         print(k, v)
