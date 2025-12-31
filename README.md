# 🚀 FlowTest Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework-API](https://img.shields.io/badge/Testing-API-blue.svg)](#)
[![No-Code](https://img.shields.io/badge/No--Code-Required-green.svg)](#)

### *Zero-Code End-to-End Backend API Testing Framework*

**FlowTest Studio** is a sophisticated, non-code required testing framework designed to bridge the gap between simple API unit testing and complex, scenario-based feature validation. 

The tool was born out of a specific need: existing tools lack the flexibility to test backend frameworks from a **scenario-wise** perspective (e.g., User Management, Enterprise Onboarding) using custom test data and handling complex **API interdependencies** where the output of one API is required as the input for another.

---

## 🌟 Key Features

* **🚫 Zero Code:** Fully GUI-driven workflow—no scripting required.
* **🔗 Interdependency Mapping:** Seamlessly pass data between APIs in a sequence.
* **📂 Postman Integration:** Direct upload of existing Postman collections.
* **📊 Scenario-Based Testing:** Group APIs into logical business flows.
* **📈 Exhaustive Reporting:** Detailed failure analysis and error code summaries.

---

## 🏗️ How It Works



[Image of API testing workflow diagram]


1.  **Initialize:** Create a project and upload your **Postman Collection**.
2.  **Define Scenarios:** Create a specific scenario (e.g., "User Onboarding").
3.  **Sequence:** Add APIs from your collection in the exact order of execution.
4.  **Connect:** Add interactions to define data flow between interdependent APIs.
5.  **Inject Data:** Upload your `.xlsx` test data file.
6.  **Execute:** Run the scenario and generate a professional test report.

---

## 🔗 Adding Interactions

FlowTest Studio handles complex dependencies through two main mechanisms:

### 1. Interaction Levels
This defines the behavior of an API within the execution flow:
* **Level 1:** Specifies inputs required when the API appears for the first time.
* **Level 2+:** Defines inputs for subsequent calls if the API is reused in the same flow.

### 2. Parameter Mapping
Users can specify parameters for **Headers**, **Params**, and **Body**. You simply map the parameter name that appears in the JSON response of the "Source API" to the input of the "Target API."

---

## 📂 Test Data Management

Test data is driven by Excel (`.xlsx`) to allow for easy bulk data entry.

### File Requirements:
* **Sheet Names:** Each sheet name must exactly match the **Scenario Name**.
* **Dynamic Placeholders:** Use `{{variable_name}}` in your Postman collection (e.g., `age: {{age}}`).
* **Formatting:** Each column corresponds to an API in the sequence, containing the JSON data for that specific call.

### 📥 Test Data Format (Example)
| Create User | Get All Users | Get User by ID | Update User |
| :--- | :--- | :--- | :--- |
| `{"{{apiKey}}": "...", "{{email}}": "a@b.com"}` | `{"{{apiKey}}": "..."}` | `{"{{apiKey}}": "..."}` | `{"{{newName}}": "Arjun"}` |
| `{"{{apiKey}}": "...", "{{email}}": "x@y.com"}` | `{"{{apiKey}}": "..."}` | `{"{{apiKey}}": "..."}` | `{"{{newName}}": "Dev"}` |

---

## 📝 Test Summary Report

At the end of every run, FlowTest Studio generates an exhaustive summary.

### **1. Executive Summary**
| Metric | Details |
| :--- | :--- |
| **Project Name** | `my_project` |
| **Scenario Name** | `User_Verification_Flow` |
| **Total APIs** | 4 |
| **Test Cases Per API** | 1 |
| **Status** | ✅ Passed: **3** | ❌ Failed: **1** |

### **2. Error Code Summary**
| Error Code | Count |
| :--- | :--- |
| 401 | 1 |

### **3. Failure Detail**
| Failed API Endpoint | Error Code | Test Case Indices |
| :--- | :--- | :--- |
| `https://api.supabase.co/rest/v1/users` | 401 | 1 |

---

## 🔮 Future Enhancements
* [ ] Support for environment-specific variables.
* [ ] Export reports to PDF/HTML.
* [ ] Integration with CI/CD pipelines (Jenkins/GitHub Actions).

---

## 👤 Author
**Arjun**
*Technical Product Manager*

---
> **Final Note:** FlowTest Studio is engineered for reliability and ease of use, ensuring that backend testing is no longer a bottleneck for development teams.
