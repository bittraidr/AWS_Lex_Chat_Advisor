
### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

def validate_data(age, investment_amount, intent_request):
    if age is not None:
        age = parse_int(age)
        if age > 64 or age < 0:
            return build_validation_result(
                False,
                "age",
                "Age cannot be zero or you must be younger than 65"
            )

    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investment_amount",
                "The amount to invest should be greater than $5,000"
            )

    return build_validation_result(True, None, None)

# Get the initial investment recommendation
def recommend_portfolio(intent_request):
    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investment_amount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]
    
    if source == "DialogCodeHook":
        slots = get_slots(intent_request)
        validation_result = validate_data(age, investment_amount, intent_request)
        
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
        
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))
    
    initial_recommendation = ""
    
    if risk_level == "None":
        initial_recommendation = "100% bonds (AGG), 0% equities (SPY)"
    elif risk_level == "Low":
        initial_recommendation = "80% bonds (AGG), 20% equities (SPY)"
    elif risk_level == "Very Low":
        initial_recommendation = "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == "Medium":
        initial_recommendation = "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == "High":
        initial_recommendation = "20% bonds (AGG), 80% equities (SPY)"
    elif risk_level == "Very High":
        initial_recommendation = "0% bonds (AGG), 100% equities (SPY)"
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": "{} thank you for your information; based on the risk level you defined, my recommendation is to choose an investment portfolio with {}"
            .format(
                first_name, initial_recommendation
            ),
        }
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")

### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """


    return dispatch(event)