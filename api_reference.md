# API Reference
Welcome to the Certify API Documentation! Almost all the functionalities of certify can be achieved with just the APIs by passing the admin dashboard and verification portal , you can use this to build your interfaces

This guide provides information about the available API endpoints, their functionalities, input data, and response formats.

Additionally, you can access the Hoppscotch API collections export from [here](https://github.com/Govind-S-B/Certify/blob/main/api_server/hoppscotch_api_test.json) documentation, allowing you to import and conduct thorough API testing firsthand.

## Overview

The base URL for all API endpoints is the same and configurable on the dockerfile

## Status

### Status

**Endpoint:** `/status`

**Description:** This endpoint returns the active status of the API.

**Method:** GET

**Response Format:**
```
{
  "active": true
}
```

## Event

### List Events

**Endpoint:** `/event/list`

**Description:** Get a list of all events.

**Method:** GET

**Response Format:**
```
[
  {
    "_id": "event_id",
    "name": "Event Name",
    "issueDt": "Date of Issue"
  },
  // ...
]
```

### Get Event Info

**Endpoint:** `/event/info`

**Description:** Get detailed information about a specific event.

**Method:** GET

**Parameters:**

-   `event_id` (Query Parameter): ID of the event to retrieve information for.

**Response Format:**
```
{
  "_id": "event_id",
  "name": "Event Name",
  "desc": "Event Description",
  "fields": ["field1", "field2"],
  "issueDt": "Date of Issue"
}
```

### Add Event

**Endpoint:** `/event/add`

**Description:** Add a new event.

**Method:** POST

**Request Body:**
```
{
  "name": "Event Name",
  "desc": "Event Description",
  "fields": ["field1", "field2"]
}
```
**Response Format:**
```
{
  "db entry status": true
}
```

### Finalize Event

**Endpoint:** `/event/finalize`

**Description:** Finalize an event by setting the issue date.

**Method:** POST

**Request Body:**
```
{
  "event_id": "event_id"
}
```
**Response Format:**
```
{
  "db entry status": true,
  "issueDt": "Date of Issue"
}
```

### Update Event

**Endpoint:** `/event/update`

**Description:** Update an event's information.

**Method:** POST

**Request Body:**
```
{
  "event_id": "event_id",
  "field": "field name",
  "value": "new value"
}
```
**Response Format:**
```
{
  "db entry status": true
}
```

### Delete Event

**Endpoint:** `/event/delete`

**Description:** Delete an event.

**Method:** DELETE

**Parameters:**

-   `event_id` (Query Parameter): ID of the event to delete.

**Response Format:**
```
{
  "db entry status": true
}
```

## Participant

### List Participants

**Endpoint:** `/participant/list`

**Description:** Get a list of participants for a specific event.

**Method:** GET

**Parameters:**

-   `event_id` (Query Parameter): ID of the event to retrieve participants for.

**Response Format:**
```
[
  {
    "_id": "participant_id",
    "event_id": "event_id",
    // other participant fields
  },
  // ...
]
```

### Get Participant Info

**Endpoint:** `/participant/info`

**Description:** Get detailed information about a specific participant.

**Method:** GET

**Parameters:**

-   `event_id` (Query Parameter): ID of the event the participant belongs to.
-   `participant_id` (Query Parameter): ID of the participant to retrieve information for.

**Response Format:**
```
{
  "_id": "participant_id",
  "event_id": "event_id",
  // other participant fields
}
```

### Add Participant

**Endpoint:** `/participant/add`

**Description:** Add a participant to an event.

**Method:** POST

**Request Body:**
```
{
  "event_id": "event_id",
  "field1": "value1",
  "field2": "value2"
}
```
**Response Format:**
```
{
  "db entry status": true
}
```

### Add Participants in Batch

**Endpoint:** `/participant/add-batch`

**Description:** Add multiple participants to an event in batch.

**Method:** POST

**Request Body:**
```
{
  "items": [
    {
      "event_id": "event_id",
      "field1": "value1 1",
      "field2": "value2 1"
    },
    {
      // ...
    },
    // ...
  ]
}
```
**Response Format:**
```
{
  "db entry status": true
}
```

### Update Participant

**Endpoint:** `/participant/update`

**Description:** Update a participant's information.

**Method:** POST

**Request Body:**
```
{
  "event_id": "event_id",
  "participant_id": "participant_id",
  "field": "field name",
  "value": "new value"
}
```
**Response Format:**
```
{
  "db entry status": true
}
```

### Delete Participant

**Endpoint:** `/participant/delete`

**Description:** Delete a participant.

**Method:** DELETE

**Parameters:**

-   `event_id` (Query Parameter): ID of the event the participant belongs to.
-   `participant_id` (Query Parameter): ID of the participant to delete.

**Response Format:**
```
{
  "db entry status": true
}
```

### Delete Participants in Batch

**Endpoint:** `/participant/delete-batch`

**Description:** Delete all participants of an event in batch.

**Method:** DELETE

**Parameters:**

-   `event_id` (Query Parameter): ID of the event to delete participants from.

**Response Format:**
```
{
  "db entry status": true
}
```

## Plugin

### Generate Information for Plugin

**Endpoint:** `/plugin/gen-info`

**Description:** Generate information in a specific format for use with a plugin.

**Method:** GET

**Parameters:**

-   `event_id` (Query Parameter): ID of the event to generate information for.

**Response Format:**
```
{
  "event": {
    "_id": "event_id",
    "name": "Event Name",
    "desc": "Event Description",
    "issueDt": "Date of Issue"
  },
  "participants": [
    {
      // participant data
    },
    // ...
  ]
}
```
