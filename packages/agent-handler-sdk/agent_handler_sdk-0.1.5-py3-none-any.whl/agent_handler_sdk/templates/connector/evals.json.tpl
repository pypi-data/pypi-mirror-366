[
    {
      "data_source_config": {
        "input_schema": {
          "type": "object",
          "properties": {
            "input": { "type": "string" },
            "reference_value": { "type": "string" },
            "reference_tools": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "args": { "type": "object" }
                },
                "required": ["name"]
              }
            }
          },
          "required": ["input"]
        }
      },
      "items": [
        {
          "input": "Tell me about George Washington",
          "reference_value": null,
          "reference_tools": [
            {
              "name": "wikipedia__search",
              "args": {
                "query": "George Washington"
              }
            }
          ]
        },
        {
          "input": "Where does London's name come from? Don't use any tools to solve this.",
          "reference_value": "London's name is believed to originate from the Latin word \"Londinium,\" which was the name used during the Roman period when the city was established as a settlement. The exact origin of \"Londinium\" is uncertain, but it may derive from a pre-Roman or Celtic word. Over time, the name evolved through various forms, such as \"Londinium\" in Latin and \"Lunden\" in Old English, eventually becoming \"London\" as we know it today.",
          "reference_tools": []
          ]
        }
      ],
      "prompts": [
        {
          "type": "text",
          "role": "user",
          "content": {
            "type": "text",
            "text": "{{input}}"
          }
        }
      ]
    }
]