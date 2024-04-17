users = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["userId", "username", "password", "email", "firstName", "lastName", "address", "phoneNumber"],
    "properties": {
      "userId": { "bsonType": "string" },
      "username": { "bsonType": "string" },
      "password": {
        "bsonType": "string",
        "minLength": 6
      },
      "email": {
        "bsonType": "string",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      },
      "firstName": { "bsonType": "string" },
      "lastName": { "bsonType": "string" },
      "address": {
        "bsonType": "object",
        "required": ["street", "city", "state", "country", "zip"],
        "properties": {
          "street": { "bsonType": "string" },
          "city": { "bsonType": "string" },
          "state": { "bsonType": "string" },
          "country": { "bsonType": "string" },
          "zip": { "bsonType": "string" }
        }
      },
      "phoneNumber": {
        "bsonType": "string",
        "pattern": "^\\(\\+92\\)\\s3[0-9]{2}\\s[0-9]{7}$"
      }
    }
  }
}
