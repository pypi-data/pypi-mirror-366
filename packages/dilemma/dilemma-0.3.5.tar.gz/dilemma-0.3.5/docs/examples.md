# Dilemma Expression Examples  
This document contains examples of using the Dilemma expression language.  
  
  
### String  
Check if a filename matches a pattern with wildcard  
  
```  
'document.pdf' like '*.pdf'  
```  
`Result: True`   

---
  
Check if two words are equal  
  
```  
'hello' is 'hello'  
```  
`Result: True`   

---
  
Check if two words are not equal  
  
```  
'hello' is not 'world'  
```  
`Result: True`   

---
  
Check if two words are not equal  
  
```  
 friend.snores is not 'often'  
```  
```json
{
  "friend": {
    "name": "Bob",
    "snores": "often"
  }
}
```  
`Result: False`   

---
  
Check if a phrase contains a word  
  
```  
'world' in 'hello world'  
```  
`Result: True`   

---
  
Check if two variables are equal  
  
```  
var1 is var2  
```  
```json
{
  "var1": "hello",
  "var2": "hello"
}
```  
`Result: True`   

---
  
Check if a string matches a pattern with ? (single character wildcard)  
  
```  
'user123' like 'user???'  
```  
`Result: True`   

---
  
Demonstrate case-insensitive matching with the &#x27;like&#x27; operator  
  
```  
'Hello.TXT' like '*.txt'  
```  
`Result: True`   

---
  
Match a variable against a pattern  
  
```  
filename like '*.jpg'  
```  
```json
{
  "filename": "vacation-photo.JPG"
}
```  
`Result: True`   

---
  
Check a variable doen&#x27;t match  a pattern  
  
```  
filename not like '*.jpg'  
```  
```json
{
  "filename": "vacation-photo.JPG"
}
```  
`Result: False`   

---
  
Check if two words are equal  
  
```  
'hello' == 'hello'  
```  
`Result: True`   

---
  
Check if two words are not equal  
  
```  
'hello' != 'world'  
```  
`Result: True`   

---
  
  
### Critical Path  
Test lookup of nested attributes by possesive English syntax  
  
```  
user's name == 'bob'  
```  
```json
{
  "user": {
    "name": "bob"
  }
}
```  
`Result: True`   

---
  
Test lookup of nested attributes by possesive English syntax  
  
```  
'admin' in user's roles   
```  
```json
{
  "user": {
    "roles": [
      "reader",
      "writer",
      "admin"
    ]
  }
}
```  
`Result: True`   

---
  
Test lookup of nested attributes by possesive English syntax  
  
```  
 user's roles contains 'reader'   
```  
```json
{
  "user": {
    "roles": [
      "reader",
      "writer",
      "admin"
    ]
  }
}
```  
`Result: True`   

---
  
Is it too late to reach the bar before last orders?  
  
```  
bar's closing_time upcoming within (bar.distance / bike.speed)  hours  
```  
```json
{
  "bar": {
    "closing_time": "__HOUR_FROM_NOW__",
    "distance": 10,
    "units": "miles"
  },
  "bike": {
    "speed": 20,
    "units": "mph"
  }
}
```  
`Result: False`   

---
  
  
### Maths  
Multiply two integers  
  
```  
8 * 8  
```  
`Result: 64`   

---
  
Divide two integers  
  
```  
64 / 8  
```  
`Result: 8`   

---
  
Add two integers  
  
```  
8 + 8  
```  
`Result: 16`   

---
  
Subtract two integers  
  
```  
8 - 8  
```  
`Result: 0`   

---
  
Multiply two floating point numbers  
  
```  
0.5 * 8.0  
```  
`Result: 4.0`   

---
  
Use variables in expressions  
  
```  
banana.price * order.quantity  
```  
```json
{
  "banana": {
    "price": 2
  },
  "order": {
    "quantity": 8
  }
}
```  
`Result: 16`   

---
  
  
### Date State  
Verify a date in the past  
  
```  
past_date is $past  
```  
```json
{
  "past_date": "2025-05-12 15:20:33 UTC"
}
```  
`Result: True`   

---
  
Verify a date in the future  
  
```  
future_date is $future  
```  
```json
{
  "future_date": "2025-05-14 15:20:33 UTC"
}
```  
`Result: True`   

---
  
Verify a date is $today  
  
```  
today_date is $today  
```  
```json
{
  "today_date": "2025-05-13 15:20:33 UTC"
}
```  
`Result: True`   

---
  
  
### Time Window  
Check event upcoming within recent hours  
  
```  
recent_event upcoming within 12 hours  
```  
```json
{
  "recent_event": "2025-05-13 14:20:33 UTC"
}
```  
`Result: True`   

---
  
Check event older than a week  
  
```  
old_event older than 1 week  
```  
```json
{
  "old_event": "2025-05-06 15:20:33 UTC"
}
```  
`Result: True`   

---
  
  
### Date Comparison  
Compare two dates with before  
  
```  
start_date before end_date  
```  
```json
{
  "start_date": "2025-05-12 15:20:33 UTC",
  "end_date": "2025-05-14 15:20:33 UTC"
}
```  
`Result: True`   

---
  
Compare two dates with after  
  
```  
end_date after start_date  
```  
```json
{
  "start_date": "2025-05-12 15:20:33 UTC",
  "end_date": "2025-05-14 15:20:33 UTC"
}
```  
`Result: True`   

---
  
Check same day (should be true)  
  
```  
same_day_morning same_day_as same_day_evening  
```  
```json
{
  "same_day_morning": "2023-05-10T08:00:00Z",
  "same_day_evening": "2023-05-10T20:00:00Z"
}
```  
`Result: True`   

---
  
Check same day (should be false)  
  
```  
different_days same_day_as other_day  
```  
```json
{
  "different_days": "2023-05-10T08:00:00Z",
  "other_day": "2023-05-11T08:00:00Z"
}
```  
`Result: False`   

---
  
  
### Complex  
Check if project is currently active  
  
```  
project_start is $past and project_end is $future  
```  
```json
{
  "project_start": "2025-05-12 15:20:33 UTC",
  "project_end": "2025-05-14 15:20:33 UTC"
}
```  
`Result: True`   

---
  
Recent login but account not new  
  
```  
last_login upcoming within 4 hours and signup_date older than 1 day  
```  
```json
{
  "last_login": "2025-05-13 14:20:33 UTC",
  "signup_date": "2025-05-12 15:20:33 UTC"
}
```  
`Result: True`   

---
  
  
### String Dates  
Compare ISO formatted date string  
  
```  
iso_date before '2030-01-01'  
```  
```json
{
  "iso_date": "2023-05-10T00:00:00Z"
}
```  
`Result: True`   

---
  
Check literal date is $past  
  
```  
'2020-01-01' is $past  
```  
`Result: True`   

---
  
Check literal date older than period  
  
```  
'2020-01-01' older than 1 year  
```  
`Result: True`   

---
  
  
### Time Units  
Use hours time unit  
  
```  
hour_ago upcoming within 2 hours  
```  
```json
{
  "hour_ago": "2025-05-13 14:20:33 UTC"
}
```  
`Result: True`   

---
  
Use minutes time unit  
  
```  
hour_ago upcoming within 120 minutes  
```  
```json
{
  "hour_ago": "2025-05-13 14:20:33 UTC"
}
```  
`Result: True`   

---
  
Use days time unit  
  
```  
week_ago older than 6 days  
```  
```json
{
  "week_ago": "2025-05-06 15:20:33 UTC"
}
```  
`Result: True`   

---
  
  
### List Operations  
Check if an element exists in a list using &#x27;in&#x27;  
  
```  
'admin' in user.roles  
```  
```json
{
  "user": {
    "roles": [
      "user",
      "admin",
      "editor"
    ],
    "name": "John Doe"
  }
}
```  
`Result: True`   

---
  
Use a variable as the item to check in a list  
  
```  
requested_role in available_roles  
```  
```json
{
  "requested_role": "manager",
  "available_roles": [
    "user",
    "admin",
    "manager",
    "guest"
  ]
}
```  
`Result: True`   

---
  
Alternative contains syntax for list membership  
  
```  
permissions contains 'delete'  
```  
```json
{
  "permissions": [
    "read",
    "write",
    "delete",
    "share"
  ]
}
```  
`Result: True`   

---
  
Check behavior when element is not in list  
  
```  
'superadmin' in user.roles  
```  
```json
{
  "user": {
    "roles": [
      "user",
      "admin",
      "editor"
    ]
  }
}
```  
`Result: False`   

---
  
  
### Object Operations  
Check if a key exists in a dictionary  
  
```  
'address' in user.profile  
```  
```json
{
  "user": {
    "profile": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "address": "123 Main St",
      "phone": "555-1234"
    }
  }
}
```  
`Result: True`   

---
  
Use a variable to check dictionary key membership  
  
```  
required_field in form_data  
```  
```json
{
  "required_field": "tax_id",
  "form_data": {
    "name": "Company Inc",
    "email": "info@company.com",
    "address": "456 Business Ave"
  }
}
```  
`Result: False`   

---
  
Use contains operator with dictionary  
  
```  
config contains 'debug_mode'  
```  
```json
{
  "config": {
    "app_name": "MyApp",
    "version": "1.2.3",
    "debug_mode": true,
    "theme": "dark"
  }
}
```  
`Result: True`   

---
  
  
### Mixed Collections  
Check membership in a list nested upcoming within a dictionary  
  
```  
'python' in user.skills.programming  
```  
```json
{
  "user": {
    "name": "Alex Developer",
    "skills": {
      "programming": [
        "javascript",
        "python",
        "go"
      ],
      "languages": [
        "english",
        "spanish"
      ]
    }
  }
}
```  
`Result: True`   

---
  
Combine collection operators with other logical operators  
  
```  
'admin' in user.roles and user.settings contains 'notifications' and user.settings.notifications  
```  
```json
{
  "user": {
    "roles": [
      "user",
      "admin"
    ],
    "settings": {
      "theme": "light",
      "notifications": true,
      "privacy": "high"
    }
  }
}
```  
`Result: True`   

---
  
  
### Collection Equality  
Compare two lists for equality  
  
```  
user.permissions == required_permissions  
```  
```json
{
  "user": {
    "permissions": [
      "read",
      "write",
      "delete"
    ]
  },
  "required_permissions": [
    "read",
    "write",
    "delete"
  ]
}
```  
`Result: True`   

---
  
Compare two dictionaries for equality  
  
```  
user.preferences == default_preferences  
```  
```json
{
  "user": {
    "preferences": {
      "theme": "dark",
      "font_size": "medium"
    }
  },
  "default_preferences": {
    "theme": "light",
    "font_size": "medium"
  }
}
```  
`Result: False`   

---
  
  
### Complex Scenarios  
Use membership test with a composite condition  
  
```  
(user.role in admin_roles) or (user.domain in approved_domains and user.verified)  
```  
```json
{
  "user": {
    "role": "manager",
    "email": "user@company.com",
    "domain": "company.com",
    "verified": true
  },
  "admin_roles": [
    "admin",
    "superadmin"
  ],
  "approved_domains": [
    "company.com",
    "partner.org"
  ]
}
```  
`Result: True`   

---
  
  
### Path Syntax  
Look up elements in arrays using indexing  
  
```  
teams[0].name == 'Frontend'  
```  
```json
{
  "teams": [
    {
      "name": "Frontend",
      "members": [
        "Alice",
        "Bob"
      ]
    },
    {
      "name": "Backend",
      "members": [
        "Charlie",
        "Dave"
      ]
    }
  ]
}
```  
`Result: True`   

---
  
Use nested array indexing in paths  
  
```  
departments[0].teams[1].name == 'Backend'  
```  
```json
{
  "departments": [
    {
      "name": "Engineering",
      "teams": [
        {
          "name": "Frontend",
          "members": [
            "Alice",
            "Bob"
          ]
        },
        {
          "name": "Backend",
          "members": [
            "Charlie",
            "Dave"
          ]
        }
      ]
    },
    {
      "name": "Marketing",
      "teams": [
        {
          "name": "Digital",
          "members": [
            "Eve",
            "Frank"
          ]
        }
      ]
    }
  ]
}
```  
`Result: True`   

---
  
Test property of an element accessed through indexing  
  
```  
users[1].role == 'admin' and users[1].verified  
```  
```json
{
  "users": [
    {
      "username": "johndoe",
      "role": "user",
      "verified": false
    },
    {
      "username": "janedoe",
      "role": "admin",
      "verified": true
    }
  ]
}
```  
`Result: True`   

---
  
Combine array indexing with membership test  
  
```  
'testing' in projects[0].tags and projects[1].status == 'completed'  
```  
```json
{
  "projects": [
    {
      "name": "Feature A",
      "tags": [
        "important",
        "testing",
        "frontend"
      ],
      "status": "in_progress"
    },
    {
      "name": "Feature B",
      "tags": [
        "backend",
        "documentation"
      ],
      "status": "completed"
    }
  ]
}
```  
`Result: True`   

---
  
  
### Complex Path Operations  
Complex expression combining array lookups with object properties  
  
```  
organization.departments[0].teams[0].members[1] == 'Bob' and organization.departments[1].teams[0].members[0] == 'Eve'  
```  
```json
{
  "organization": {
    "name": "Acme Corp",
    "departments": [
      {
        "name": "Engineering",
        "teams": [
          {
            "name": "Frontend",
            "members": [
              "Alice",
              "Bob"
            ]
          },
          {
            "name": "Backend",
            "members": [
              "Charlie",
              "Dave"
            ]
          }
        ]
      },
      {
        "name": "Marketing",
        "teams": [
          {
            "name": "Digital",
            "members": [
              "Eve",
              "Frank"
            ]
          }
        ]
      }
    ]
  }
}
```  
`Result: True`   

---
  
  
### Container Operations  
Check if containers are empty using &#x27;is $empty&#x27;  
  
```  
ghost_crew is $empty and deserted_mansion is $empty and (treasure_chest is $empty) == false  
```  
```json
{
  "ghost_crew": [],
  "treasure_chest": [
    "ancient coin",
    "golden chalice",
    "ruby necklace"
  ],
  "deserted_mansion": {},
  "dragon_hoard": {
    "golden_crown": 1500,
    "enchanted_sword": 3000,
    "crystal_orb": 750
  }
}
```  
`Result: True`   

---
  
  
### Nested Objects  
Check if user is eligible for premium features  
  
```  
user.account.is_active and (user.subscription.level == 'premium' or user.account.credits > 100)  
```  
```json
{
  "user": {
    "account": {
      "is_active": true,
      "credits": 150,
      "created_at": "2025-05-06 15:20:33 UTC"
    },
    "subscription": {
      "level": "basic",
      "renewal_date": "2025-06-12 15:20:33 UTC"
    }
  }
}
```  
`Result: True`   

---
  
Evaluate complex project status conditions  
  
```  
project.status == 'in_progress'
and (
  project.metrics.completion > 50
  or (project.team.size >= 3 and project.priority == 'high')
)
  
```  
```json
{
  "project": {
    "status": "in_progress",
    "start_date": "2025-05-06 15:20:33 UTC",
    "deadline": "2025-06-12 15:20:33 UTC",
    "metrics": {
      "completion": 45,
      "quality": 98
    },
    "team": {
      "size": 5,
      "lead": "Alice"
    },
    "priority": "high"
  }
}
```  
`Result: True`   

---
  
  
### Mixed Date Logic  
Check if order is eligible for express shipping  
  
```  
order.status == 'confirmed'
and order.created_at upcoming within 24 hours
and (
  order.items.count < 5
  or (order.customer.tier == 'gold' and order.total_value > 100)
)
  
```  
```json
{
  "order": {
    "status": "confirmed",
    "created_at": "2025-05-13 14:20:33 UTC",
    "items": {
      "count": 7,
      "categories": [
        "electronics",
        "books"
      ]
    },
    "customer": {
      "tier": "gold",
      "since": "2025-05-06 15:20:33 UTC"
    },
    "total_value": 250
  }
}
```  
`Result: True`   

---
  
Multiple date conditions with nested properties  
  
```  
(user.last_login upcoming within 7 days or user.auto_login)
and (
  user.account.trial_ends is $future
  or
  user.account.subscription.status == 'active'
)
  
```  
```json
{
  "user": {
    "last_login": "2025-05-06 15:20:33 UTC",
    "auto_login": true,
    "registration_date": "2023-01-15",
    "account": {
      "trial_ends": "2025-05-12 15:20:33 UTC",
      "subscription": {
        "status": "active",
        "plan": "premium",
        "next_payment": "2025-06-12 15:20:33 UTC"
      }
    }
  }
}
```  
`Result: True`   

---
  
  
### Complex Precedence  
Test operator precedence with mixed conditions  
  
```  
user.settings.notifications.enabled
and (user.last_seen older than 1 day or user.preferences.urgent_only)
and ('admin' in user.roles or user.tasks.pending > 0)
  
```  
```json
{
  "user": {
    "settings": {
      "notifications": {
        "enabled": true,
        "channels": [
          "email",
          "push"
        ]
      },
      "theme": "dark"
    },
    "last_seen": "2025-05-06 15:20:33 UTC",
    "preferences": {
      "urgent_only": false,
      "language": "en"
    },
    "roles": "user, admin",
    "tasks": {
      "pending": 3,
      "completed": 27
    }
  }
}
```  
`Result: True`   

---
  
  
### Jq Basics  
Basic JQ expression to access a nested property  
  
```  
`.user.profile.name` == 'Alice'  
```  
```json
{
  "user": {
    "profile": {
      "name": "Alice",
      "age": 32
    },
    "settings": {
      "notifications": true
    }
  }
}
```  
`Result: True`   

---
  
  
### Jq Arrays  
Access elements in an array using JQ indexing  
  
```  
`.team[1].role` == 'developer'  
```  
```json
{
  "team": [
    {
      "name": "Bob",
      "role": "manager"
    },
    {
      "name": "Charlie",
      "role": "developer"
    },
    {
      "name": "Diana",
      "role": "designer"
    }
  ]
}
```  
`Result: True`   

---
  
Check array length using JQ pipe function  
  
```  
`.products | length` > 2  
```  
```json
{
  "products": [
    {
      "id": 101,
      "name": "Laptop"
    },
    {
      "id": 102,
      "name": "Phone"
    },
    {
      "id": 103,
      "name": "Tablet"
    }
  ]
}
```  
`Result: True`   

---
  
Check if any array element matches a condition  
  
```  
`.users[] | select(.role == "admin") | .name` == 'Eva'  
```  
```json
{
  "users": [
    {
      "name": "Dave",
      "role": "user"
    },
    {
      "name": "Eva",
      "role": "admin"
    },
    {
      "name": "Frank",
      "role": "user"
    }
  ]
}
```  
`Result: True`   

---
  
  
### Jq Filtering  
Filter array elements based on a condition  
  
```  
`.orders[] | select(.status == "completed") | .id` == 1003  
```  
```json
{
  "orders": [
    {
      "id": 1001,
      "status": "pending"
    },
    {
      "id": 1002,
      "status": "processing"
    },
    {
      "id": 1003,
      "status": "completed"
    }
  ]
}
```  
`Result: True`   

---
  
  
### Jq Mixed  
Combine JQ with regular Dilemma expressions  
  
```  
`.user.membership.level` == 'gold' and user.account.active == true  
```  
```json
{
  "user": {
    "membership": {
      "level": "gold",
      "since": "2025-05-06 15:20:33 UTC"
    },
    "account": {
      "active": true,
      "credits": 500
    }
  }
}
```  
`Result: True`   

---
  
  
### Jq Advanced  
Complex data transformation with JQ  
  
```  
`.departments[] | select(.name == "Engineering").employees | map(.salary) | add / length` > 75000  
```  
```json
{
  "departments": [
    {
      "name": "Marketing",
      "employees": [
        {
          "name": "Grace",
          "salary": 65000
        },
        {
          "name": "Henry",
          "salary": 68000
        }
      ]
    },
    {
      "name": "Engineering",
      "employees": [
        {
          "name": "Isla",
          "salary": 78000
        },
        {
          "name": "Jack",
          "salary": 82000
        },
        {
          "name": "Kate",
          "salary": 80000
        }
      ]
    }
  ]
}
```  
`Result: True`   

---
  
Check if an array contains a specific value  
  
```  
`.user.permissions | contains(["edit"])`  
```  
```json
{
  "user": {
    "id": 1234,
    "name": "Lucy",
    "permissions": [
      "read",
      "edit",
      "share"
    ]
  }
}
```  
`Result: True`   

---
  
Use JQ to conditionally create and check an object  
  
```  
`if .user.premium then {access: "full"} else {access: "limited"} end | .access` == 'full'  
```  
```json
{
  "user": {
    "premium": true,
    "account_type": "business"
  }
}
```  
`Result: True`   

---
  
Complex JQ expression with deeply nested parentheses and operations  
  
```  
`.employees | map( ((.performance.rating * 0.5) + ((.projects | map(select(.status == "completed") | .difficulty) | add // 0) * 0.3) + (if (.years_experience > 5) then ((.leadership_score // 0) * 0.2) else ((.learning_speed // 0) * 0.2) end) ) * (if .department == "Engineering" then 1.1 else 1 end) ) | add / length` > 75  
```  
```json
{
  "employees": [
    {
      "name": "Alice",
      "department": "Engineering",
      "performance": {
        "rating": 98
      },
      "projects": [
        {
          "name": "Project A",
          "status": "completed",
          "difficulty": 9
        },
        {
          "name": "Project B",
          "status": "completed",
          "difficulty": 10
        }
      ],
      "years_experience": 7,
      "leadership_score": 95
    },
    {
      "name": "Bob",
      "department": "Engineering",
      "performance": {
        "rating": 95
      },
      "projects": [
        {
          "name": "Project C",
          "status": "completed",
          "difficulty": 8
        },
        {
          "name": "Project D",
          "status": "in_progress",
          "difficulty": 10
        }
      ],
      "years_experience": 4,
      "learning_speed": 98
    },
    {
      "name": "Charlie",
      "department": "Marketing",
      "performance": {
        "rating": 98
      },
      "projects": [
        {
          "name": "Project E",
          "status": "completed",
          "difficulty": 10
        },
        {
          "name": "Project F",
          "status": "completed",
          "difficulty": 8
        }
      ],
      "years_experience": 6,
      "leadership_score": 90
    }
  ]
}
```  
`Result: True`   

---
  
  
### Jq With Dates  
Use JQ to extract a date for comparison  
  
```  
`.project.milestones[] | select(.name == "beta").date` is $past  
```  
```json
{
  "project": {
    "name": "Product Launch",
    "milestones": [
      {
        "name": "alpha",
        "date": "2025-06-12 15:20:33 UTC"
      },
      {
        "name": "beta",
        "date": "2025-05-12 15:20:33 UTC"
      },
      {
        "name": "release",
        "date": "2025-05-13 17:20:33 UTC"
      }
    ]
  }
}
```  
`Result: True`   

---
  
  
### Jq Parsing  
Simple JQ expression nested inside multiple levels of Dilemma parentheses  
  
```  
(5 + ((`.users | length` * 2) - 1)) > 5  
```  
```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice"
    },
    {
      "id": 2,
      "name": "Bob"
    },
    {
      "id": 3,
      "name": "Charlie"
    }
  ]
}
```  
`Result: True`   

---
  
