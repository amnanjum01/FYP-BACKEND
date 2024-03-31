{
    "$jsonSchema": {
      "required": [
        "productName",
        "sku",
        "priceOfProduct",
        "description",
        "label",
        "vector",
        "imagePath"
      ],
      "properties": {
        "productName": { "bsonType": "string" },
        "sku": { "bsonType": "string" },
        "priceOfProduct": { "bsonType": "int" },
        "description": { "bsonType": "string" },
        "label": { "bsonType": "string" },
        "vector": { "bsonType": "string" },
        "likes": { "bsonType": "int" },
        "shares": { "bsonType": "int" },
        "sizes": {
          "bsonType": "array",
          "items": {
            "bsonType": "object",
            "required": ["size", "quantity"],
            "properties": {
              "size": { "bsonType": "string" },
              "quantity": { "bsonType": "int" }
            }
          }
        },
        "imagePath": {
          "bsonType": "array",
          "items": {
            "bsonType": "object",
            "required": ["imgUrl", "imgPath"],
            "properties": {
              "imgUrl": { "bsonType": "string" },
              "imgPath": { "bsonType": "string" }
            }
          }
        },
        "reviews": {
          "bsonType": "array",
          "items": {
            "bsonType": "object",
            "required": ["rating", "reviewText"],
            "properties": {
              "rating": { "bsonType": "int" },
              "reviewText": { "bsonType": "string" }
            }
          }
        },
        "tags": {
          "bsonType": "array",
          "items": {
            "bsonType": "string"
          }
        }
      }
    }
  }
  