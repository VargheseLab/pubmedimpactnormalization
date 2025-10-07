import asyncio
import datetime
import time
import aiohttp


### This is direct API calls
async def ncbi_search(ncbi_api_limiter, search_term, min_year=2000, cur_year=datetime.date.today().year, agg_years=1, api_key='', skip_curr_year=True):
    if api_key:
        api_key = f'&api_key={api_key}'

    search_term = search_term.replace(' ', '%20') #allow whitespaces
    base_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&rettype=count{api_key}&term={search_term}'
    urls = [f'{base_url}%20AND%20({date-agg_years+1}[PDAT]%20OR%20{date}[PDAT])' for date in range(cur_year-skip_curr_year, min_year, -agg_years)]

    async with aiohttp.ClientSession() as session:
        reponses = await asyncio.gather(*[ncbi_api_limiter()(session, url) for url in urls])

    processed_data = [["Year", "Amount"], *reponses] # add required header
    return processed_data



class NCBI_API_Limiter:
    def __init__(self, rate_limit: int = 3, period: float = 1.2):
        self.rate_limit = rate_limit
        self.period = period
        self.requests_finish_time = 0
        self.semaphore = asyncio.Semaphore(rate_limit)
        self.barrier = asyncio.Barrier(rate_limit)
        self.func = _ncbi_api_call

    def update_limits(self, rate_limit):
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(rate_limit)
        self.barrier = asyncio.Barrier(rate_limit)

    async def sleep(self):
        sleep_before = self.requests_finish_time
        now = time.monotonic()
        if sleep_before >= now:
            await asyncio.sleep(sleep_before - now)

    def __call__(self):
        async def wrapper(*args, **kwargs):
            async with self.semaphore:
                await self.sleep()
                res = await self.func(*args, **kwargs)
                if self.semaphore.locked():
                    pos = await self.barrier.wait() # additional barrier, as it counts only after all requests
                    if pos == 0:
                        self.requests_finish_time = (time.monotonic() + self.period)

            return res

        return wrapper


async def _ncbi_api_call(session, url, allow_retry=True):
    year = url[-11:-7]
    async with session.get(url=url) as response:

        body = await response.text()
        if "API rate limit exceeded" in body:
            if allow_retry: 
                await asyncio.sleep(1.5)
                return await _ncbi_api_call(session, url, allow_retry=True)
            else: return [None, None]
        body = body[body.find('<Count>') + 7 : ]
        body = body[: body.find('</Count>') ]
    return [year, int(body)]
###