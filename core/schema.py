import graphene
import tickets.schema as tickets_schema

class Query(tickets_schema.Query, graphene.ObjectType):
    # hello = graphene.String(default_value="Hi!")
    pass

schema = graphene.Schema(query=Query)