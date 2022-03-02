import os
from dotenv import load_dotenv
from flask import Flask, request, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId

from .model import Asset
from .objectid import PydanticObjectId

load_dotenv()
dburi = os.getenv('DB_URI')

client = MongoClient(dburi,
                     tls=True,
                     tlsCertificateKeyFile='certs\X509-cert-100259875534053013.pem')

db = client.get_database('deskioDB')

companies_col = db.companies
assets_col = db.assets

app = Flask(__name__)

@app.route("/assets/")
def list_assets():
    """
    GET a list of assets.
    The results are paginated using the `page` parameter.
    """

    page = int(request.args.get("page", 1))
    per_page = 10  # A const value.

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    cursor = assets_col.find().sort("name").skip(per_page * (page - 1)).limit(per_page)

    asset_count = assets_col.count_documents({})

    links = {
        "self": {"href": url_for(".list_assets", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_assets", page=(asset_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_assets", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < asset_count // per_page:
        links["next"] = {
            "href": url_for(".list_assets", page=page + 1, _external=True)
        }

    return {
        "assets": [Asset(**doc).to_json() for doc in cursor],
        "_links": links,
    }

@app.route("/assets/<string:slug>", methods=["GET"])
def get_cocktail(slug):
    asset = assets_col.find_one({"slug": slug})
    return Asset(**asset).to_json()

app.route("/assets/", methods=["POST"])
def new_asset():
    raw_asset = request.get_json()
    raw_asset["date_added"] = datetime.utcnow()

    asset = Asset(**raw_asset)
    insert_result = assets_col.insert_one(asset.to_bson())
    asset.id = PydanticObjectId(str(insert_result.inserted_id))
    print(asset)

    return asset.to_json()



@app.route("/assets/<string:slug>", methods=["PUT"])
def update_cocktail(slug):
    asset = Asset(**request.get_json())
    asset.date_updated = datetime.utcnow()
    updated_doc = assets_col.find_one_and_update(
        {"slug": slug},
        {"$set": asset.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return Asset(**updated_doc).to_json()
    else:
        flask.abort(404, "Asset not found")


@app.route("/assets/<string:slug>", methods=["DELETE"])
def delete_asset(slug):
    deleted_asset = assets_col.find_one_and_delete(
        {"slug": slug},
    )
    if deleted_asset:
        return Asset(**deleted_asset).to_json()
    else:
        flask.abort(404, "Asset not found")




@app.route('/company/<companyname>')
def get_company(companyname):
    company = companies_col.find_one({ 'name' : str(companyname)})
    return {
        'company' : company['name'],
        'phone': company['phone']
    }


@app.route('/asset/<assetId>')
def get_asset(assetId):
    asset = deskioDB.assets.find_one({ '_id' :  ObjectId(assetId) })
    asset = parse_json(asset)
    return {
        'id' :  asset[str('_id')],
        'companyName' : asset['companyName'],
        'type' : asset['type'],
        'friendlyName' : asset['friendlyName'],
        'companyId' : asset['companyId']
    }
