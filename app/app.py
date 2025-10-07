
import asyncio
import os
from flask import Flask, jsonify, request, render_template
from sqlalchemy import Column, Integer, PickleType, String
from utils.ncbi_api import NCBI_API_Limiter, ncbi_search
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


from utils.plots import plot

# Create Application
app = Flask(__name__)
global request_handler

env_settings = os.environ.get("SET_SETTINGS", False)
skip_curr_year = os.environ.get("SKIP_CURRENT_YEAR", True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////instance/project.db"

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Terms(db.Model):
    term = Column(String, primary_key=True)
    agg_years = Column(Integer, primary_key=True)
    values = Column(PickleType)

with app.app_context():
    db.create_all()


## routes
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/api', methods=['GET', 'POST'])
async def api():
    query_term = request.form.get('query_term')
    ref_term = request.form.get('ref_term')

    if not env_settings:
        api_key = request.form.get('api_key', '')
        rate_limit = request.form.get('rate_limit', 3)
        agg_years = request.form.get('agg_years', 1)
    else:
        api_key = os.environ.get("NCBI_API_KEY", "")
        rate_limit = os.environ.get("NCBI_RATE_LIMIT", 3)
        agg_years = os.environ.get("AGGREGATION_YEARS", 1)

    if query_term is None or ref_term is None:
        return render_template("index.html")

    return await request_handler.normalize_pubmed_query(query_term, ref_term, api_key, int(rate_limit), int(agg_years))


@app.route('/settings', methods=['GET', 'POST'])
def get_settings():
    if env_settings:
        return jsonify(True)
    else:
        return jsonify(False)

    
class RequestHandler():
    def __init__(self, api_key='', rate_limit=3, skip_curr_year=True):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.skip_curr_year = skip_curr_year

    async def normalize_pubmed_query(self, query_term, ref_term, api_key, rate_limit, agg_years):
        all_values = list(db.session.execute(db.select(Terms.term, Terms.agg_years)))
        ncbi_api_limiter = NCBI_API_Limiter(rate_limit=rate_limit)   #reinitialisation of event loop Barriers

        if (query_term, agg_years) not in all_values: 
            query = await self._search_ncbi(ncbi_api_limiter, query_term, api_key, agg_years, self.skip_curr_year)
            new_term = Terms(
                term=query_term,
                agg_years=agg_years,
                values=query,
            )
            db.session.add(new_term)
        else: 
            query = db.session.get(Terms, (query_term, agg_years))
            if query: query = query.values

        if (ref_term, agg_years) not in all_values: 
            ref = await self._search_ncbi(ncbi_api_limiter, ref_term, api_key, agg_years, self.skip_curr_year)
            new_term = Terms(
                term=ref_term,
                agg_years=agg_years,
                values=ref,
            )
            db.session.add(new_term)
        else: 
            ref = db.session.get(Terms, (ref_term, agg_years))
            if ref: ref = ref.values

        if query is None or ref is None:
            return jsonify({})

        db.session.commit()
        return plot(query, ref, query_term, ref_term, agg_years)

    async def _search_ncbi(self, ncbi_api_limiter, term, api_key, agg_years, skip_curr_year):
        search_results = dict(await ncbi_search(ncbi_api_limiter, search_term=term, api_key=api_key, agg_years=agg_years, skip_curr_year=skip_curr_year))
        return {key: float(search_results[key]) for key in search_results.keys() if isinstance(search_results[key], int)}


request_handler = RequestHandler(skip_curr_year)