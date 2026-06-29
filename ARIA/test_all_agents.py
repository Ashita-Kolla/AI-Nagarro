import os
from dotenv import load_dotenv

# Mock human_gate before importing AgentRunner
import core.hitl
def mocked_human_gate(agent_name):
    print(f"\n[MOCK HUMAN GATE] Automatically approving {agent_name}")
    return 'A', None
core.hitl.human_gate = mocked_human_gate

from core.supervisor import Supervisor
from core.context_manager import ContextManager
from core.agent_runner import AgentRunner
from core.agent_registry import AGENT_REGISTRY

load_dotenv(override=True)

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found.")
        return

    test_prompt = """
    # Project Brief: Contact Management Web Application

## Project Overview

Build a simple web-based Contact Management application that allows users to store, view, update, and delete personal or business contacts. The application should provide an intuitive interface for managing contact information and support basic CRUD operations.

## Target Audience

* Individual users
* Freelancers
* Small business owners

## Business Goal

Provide a lightweight solution for organizing and managing contact information in a centralized location.

---

## Functional Requirements

### Contact Management

Users should be able to:

* Create a new contact
* View all contacts
* View contact details
* Edit existing contacts
* Delete contacts

### Contact Information

Each contact should contain:

* Full Name (Required)
* Email Address (Required)
* Phone Number (Required)
* Company Name (Optional)
* Notes (Optional)

### Dashboard

* Display a list of all contacts
* Show total number of contacts
* Allow searching contacts by name

---

## Frontend Requirements

### General Design

* Clean and modern interface
* Responsive design for desktop and tablet devices
* Simple navigation with minimal clicks
* Consistent spacing, typography, and styling

### Dashboard Page

The main page should contain:

#### Header

* Application title: "Contact Manager"
* Search bar for filtering contacts by name

#### Summary Section

* Card displaying total number of contacts

#### Contact List Section

Display contacts in a table or card layout showing:

* Full Name
* Email Address
* Phone Number
* Company Name

Each contact should have:

* View button
* Edit button
* Delete button

#### Add Contact Button

A prominent button allowing users to create a new contact.

### Create Contact Page

Provide a form containing:

* Full Name
* Email Address
* Phone Number
* Company Name
* Notes

Actions:

* Save Contact
* Cancel

### Edit Contact Page

* Pre-populate existing contact information
* Allow users to update details
* Save changes

### Contact Details Page

Display all information related to a selected contact in a readable format.

---

## Backend Requirements

### API Responsibilities

The backend should:

* Manage contact data
* Validate incoming requests
* Handle CRUD operations
* Return appropriate HTTP status codes
* Expose RESTful API endpoints


### Validation Rules

* Full Name cannot be empty
* Email must be a valid email address
* Phone Number cannot be empty
* Contact IDs must be unique

### Error Handling

The API should return meaningful error responses for:

* Invalid input
* Contact not found
* Server errors

---

## Non-Functional Requirements

### Usability

* Easy to learn and use
* Minimal user actions required
* Responsive design

### Performance

* Contact list should load within 2 seconds
* Search results should appear instantly

### Security

* Validate all user inputs
* Prevent malformed requests
* Follow secure API development practices

---

## Technology Stack

### Frontend

* React
* Tailwind CSS

### Backend

* FastAPI (Python)

### API Style

* REST API

### Development Tools

* Git
* Docker

---

## Budget

USD $3,000

---

## Timeline

- 6 weeks

## Out of Scope

* User authentication
* User roles
* Email notifications
* File uploads
* Third-party integrations
* Mobile application
* Analytics dashboard

---

## Expected Deliverables

1. Requirements Document
2. System Architecture
3. FastAPI Backend
4. React Frontend
5. REST API Documentation
6. Test Cases
7. Docker Configuration
8. Deployment Guide

    """

    print("Starting automated test run of all agents...")
    
    context_manager = ContextManager()
    # Reset context for a fresh run
    context_manager.project_context = {}
    context_manager.add_output("USER_BRIEF", test_prompt.strip())
    
    supervisor = Supervisor()
    runner = AgentRunner(context_manager, supervisor)
    
    # We want to run ALL agents in order
    standard_order = ["BA", "Architect", "Planner", "Developer", "Environment", "QA", "DevOps", "PM", "Optimisation"]
    
    print(f"Queue: {standard_order}")
    runner.run_queue(standard_order, start_index=0)
    
    print("\n--- Test Run Completed ---")
    print("Check outputs/full_project_context.json for the final combined output.")

if __name__ == "__main__":
    main()
