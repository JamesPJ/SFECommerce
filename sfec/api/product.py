# -*- coding: utf-8 -*-

from flask.ext.restful import fields

from app import api
from sfec.api.base import BaseResource
from sfec.api.decorators import FinalResource
from sfec.models.product import Product, Category
from flask.ext.restful import reqparse
from sfec.database.runtime import get_default_store
from sfec.controllers.decorators import require_vendor
from decimal import Decimal
from storm.expr import In


@FinalResource
class ProductResource(BaseResource):

    properties = {
        'id': fields.Integer,
        'name': fields.String,
        'stock': fields.Integer,
        'description': fields.String,
        'price': fields.Float,
        'is_available': fields.Boolean,
        'category_list': fields.List(fields.String),
    }

    table = Product

    order_by = Product.name

    filters = {
        'id': Product.id,
        'name': Product.name,
    }

    @require_vendor
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('stock', type=int, required=True)
        parser.add_argument('description', type=unicode, required=True)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('is_available', type=bool, required=True)
        parser.add_argument('categories', type=int, required=True, action='append')
        args = parser.parse_args()
        store = get_default_store()

        p = Product()
        p.name = args['name']
        p.stock = args['stock']
        p.description = args['description']
        p.price = Decimal(args['price'])
        p.is_available = args['is_available']
        cats = store.find(Category, In(Category.id, args['categories']))
        for c in cats:
            p.categories.add(c)
        store.add(p)
        store.commit()
        return "Success",201

    @require_vendor
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        store = get_default_store()
        p = store.find(Product, Product.id == args['id']).one()
        if p is None:
            return "Fail",404
        store.remove(p)
        store.commit()
        return "Success",204

    @require_vendor
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('stock', type=int, required=True)
        parser.add_argument('description', type=unicode, required=True)
        parser.add_argument('price', type=float, required=True)
        parser.add_argument('is_available', type=bool, required=True)
        parser.add_argument('categories', type=int, required=True, action='append')
        args = parser.parse_args()
        store = get_default_store()

        p = store.find(Product, Product.id == args['id']).one()
        if p is None:
            return "Fail",404
        p.name = args['name']
        p.stock = args['stock']
        p.description = args['description']
        p.price = Decimal(args['price'])
        p.is_available = args['is_available']
        p.categories.clear()
        cats = store.find(Category, In(Category.id, args['categories']))
        for c in cats:
            p.categories.add(c)
        store.flush()
        return "Success",201

    def get(self, id=None):
        sup = super(ProductResource,self).get(id)

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=False)
        parser.add_argument('categories', type=int, required=False, action='append')
        args = parser.parse_args()

        if args['categories']:
            categories = args['categories']
            return [r for r in sup
                    if set([c.id for c in r.categories]) & set(categories) ==
                       set(categories)]
        else:
            return sup


@FinalResource
class CategoryResource(BaseResource):

    properties = {
        'id': fields.Integer,
        'name': fields.String
    }

    table = Category

    order_by = Category.name

    filters = {
        'id': fields.Integer,
        'name': Category.name,
    }

    @require_vendor
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, required=True)
        args = parser.parse_args()
        c = Category(args['name'])
        store = get_default_store()
        store.add(c)
        store.commit()
        return "Success",201

    @require_vendor
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        store = get_default_store()
        c = store.find(Category, Category.id == args['id']).one()
        if c is None:
            return "Fail",404
        store.remove(c)
        store.commit()
        return "Success",204

    @require_vendor
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('name', type=unicode, required=True)
        args = parser.parse_args()
        store = get_default_store()
        c = store.find(Category, Category.id == args['id']).one()
        if c is None:
            return "Fail",404
        c.name = args['name']
        store.flush()
        return "Success",201




def register_product_resource():
    api.add_resource(ProductResource, '/products', endpoint='products')
    api.add_resource(CategoryResource, '/categories', endpoint='categories')
