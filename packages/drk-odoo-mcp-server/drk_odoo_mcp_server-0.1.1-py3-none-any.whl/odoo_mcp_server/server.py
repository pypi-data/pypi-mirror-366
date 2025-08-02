from fastmcp import FastMCP
import os
import odoorpc
from typing import List, Dict, Optional, Any

email = os.getenv("ODOO_EMAIL")
password = os.getenv("ODOO_PASSWORD")
database = os.getenv("ODOO_DATABASE")
url = os.getenv("ODOO_URL", "localhost")
port = int(os.getenv("ODOO_PORT", 443))
protocol = os.getenv("ODOO_PROTOCOL", "jsonrpc+ssl")

mcp = FastMCP(name="odoo-mcp-server",
              instructions="""
              Odoo MCP Server for CRM tools.
              """
              )

def connect(url: str, db: str, email: str, password: str, port: int = 443, protocol: str = 'jsonrpc+ssl'):
    """Connect to Odoo instance."""
    try:
        odoo = odoorpc.ODOO(url, protocol=protocol, port=port)
        odoo.login(db, email, password)
        user = odoo.env.user
        print(f"Connected to Odoo as {user.name} of {user.company_id.name}")
        return odoo
    
    except Exception as e:
        raise Exception(f"Failed to connect to Odoo: {e}")

@mcp.tool
def get_leads(filters: Optional[List] = None, fields: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
    """
    Retrieve a list of leads from the Odoo CRM module using optional filters.

    Args:
        filters (list, optional): A list of domain filter tuples to filter the leads.
            Example: [('email_from', '=', 'john@example.com')].
            Defaults to an empty list, meaning no filtering.
        fields (list, optional): A list of field names (strings) to include in the result.
            Defaults to ['name', 'email_from', 'stage_id'].
        limit (int, optional): Maximum number of leads to retrieve. Defaults to 10.

    Returns:
        list[dict]: A list of dictionaries, each representing a lead with the specified fields.
            Each dictionary contains keys matching the `fields` list.
    
    Example:
        >>> get_leads(filters=[('name', 'ilike', 'John')], fields=['name', 'email_from'])
        [{'name': 'John Doe', 'email_from': 'john@example.com'}, ...]
    
    """
    print("Connecting to server..")
    odoo = connect(url, database, email, password, port, protocol)
    lead = odoo.env['crm.lead']
    filters = filters or []
    fields = fields or ['name', 'email_from', 'stage_id']
    return lead.search_read(filters, fields, limit=limit)

@mcp.tool
def create_lead(lead_data: Dict[str, Any]) -> int:
    """
       Create a new lead in the Odoo CRM module.

    Args:
        odoo (odoorpc.ODOO): An active OdooRPC connection instance.

        lead_data (dict): A dictionary containing the field values for the new lead.
            Keys must correspond to fields in the 'crm.lead' model.

            Common fields and expected types:
            ---------------------------------
            - name (str): The title or name of the lead (e.g., "John Doe")
            - email_from (str): Email address of the contact (e.g., "john@example.com")
            - phone (str): Contact phone number (e.g., "1234567890")
            - description (str): A free text description or notes (e.g., "Interested in product X")
            - type (str): Type of lead: 'lead' (default) or 'opportunity'
            - priority (str): Priority level: '0' (Low), '1' (Normal), '2' (High), '3' (Very High)
            - stage_id (int): ID of the pipeline stage
            - user_id (int): ID of the assigned sales user
            - team_id (int): ID of the sales team
            - expected_revenue (float): Expected revenue from the deal
            - date_deadline (str): Deadline in 'YYYY-MM-DD' format
            - partner_name (str): Name of the company/contact
            - contact_name (str): Name of the individual contact person

            Example:
                {
                    'name': 'John Doe',
                    'email_from': 'john@example.com',
                    'phone': '1234567890',
                    'type': 'lead',
                    'priority': '2',
                    'description': 'Wants demo of new feature set',
                    'expected_revenue': 15000.0,
                    'date_deadline': '2025-08-15',
                    'team_id': 3,
                    'user_id': 7
                }

    Returns:
        int: The ID of the newly created lead.

    Example:
        >>> create_lead(odoo, {
        ...     'name': 'New Lead',
        ...     'email_from': 'test@example.com',
        ...     'type': 'opportunity',
        ...     'priority': '1'
        ... })
        42
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    lead_id = Lead.create(lead_data)
    return lead_id

@mcp.tool
def update_lead(lead_id: int, updates: dict) -> bool:
    """
    
    Updates a lead's information in Odoo based on the given lead ID.

    This function uses the `crm.lead` model to perform a partial update.
    Only the fields provided in the `updates` dictionary will be changed;
    all other fields will remain unchanged.

    Args:
        odoo (odoorpc.ODOO): An active OdooRPC connection instance.
        lead_id (int): The ID of the lead to update.
        update_data (dict): A dictionary of fields to update. Keys must match fields in the 'crm.lead' model.

            Common updatable fields:
            -------------------------
            - name (str): Updated title or name
            - email_from (str): Updated email address
            - phone (str): Updated phone number
            - description (str): Updated notes or context
            - stage_id (int): New pipeline stage ID
            - user_id (int): New assigned user ID
            - team_id (int): New sales team ID
            - expected_revenue (float): Revised expected revenue
            - date_deadline (str): New deadline in 'YYYY-MM-DD' format
            - priority (str): New priority level: '0', '1', '2', or '3'
            - type (str): Either 'lead' or 'opportunity'

            Example:
                {
                    'description': 'Followed up on call. Awaiting response.',
                    'stage_id': 5,
                    'priority': '3'
                }

    Returns:
        bool: True if the update was successful, False otherwise.

    Example:
        >>> update_lead(odoo, 42, {'stage_id': 5, 'priority': '2'})
        True

    Notes:
        - You can pass only the fields you wish to update. All unspecified fields
          will remain unchanged.
        - Ensure the lead ID exists before calling this function to avoid errors.
        - This function assumes access to the global `odoo` connection object.
    
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    try:
        lead_data = Lead.read([lead_id])
        if not lead_data:
            raise ValueError(f"No lead found with ID {lead_id}")
    except Exception:
        raise ValueError(f"Failed to retrieve lead with ID {lead_id}")

    return Lead.write([lead_id], updates)

@mcp.tool
def delete_lead(lead_id: int) -> bool:
    """
    Deletes a lead from the Odoo CRM system based on its unique ID.

    This function permanently removes a lead record from the `crm.lead` model in Odoo.
    It should be used with caution, as deletion cannot be undone.
    Only users with the appropriate access rights can delete leads.

    Parameters:
    ----------
    lead_id : int
        The unique identifier (ID) of the lead to delete.
        Example: If the lead with ID `7` exists, `delete_lead(7)` will attempt to delete it.

    Returns:
    -------
    bool
        Returns True if the lead was successfully deleted.
        Returns False if the lead was not found or deletion failed.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    lead_ids = Lead.search([('id', '=', lead_id)])

    if not lead_ids:
        return False

    return Lead.unlink(lead_ids)

@mcp.tool
def get_lead_by_id(lead_id: int, fields: list[str] = None) -> dict:
    """
    Retrieves a specific lead's information from the Odoo CRM system using its unique ID.

    This function searches for a lead in the `crm.lead` model by its primary key (ID) and 
    returns its information. You can specify which fields you want to retrieve.

    Parameters:
    ----------
    lead_id : int
        The unique identifier of the lead you want to retrieve.
        Example: `get_lead_by_id(12)` will fetch the lead with ID 12.

    fields : list[str], optional
        A list of field names to return. If not provided, defaults to:
        ['name', 'email_from', 'stage_id'].
        Example: ['name', 'email_from', 'phone', 'user_id']

    Returns:
    -------
    dict
        A dictionary representing the lead's data. Returns an empty dictionary if no lead is found.
        Example:
        {
            'id': 12,
            'name': 'John Doe',
            'email_from': 'john@example.com',
            'stage_id': [3, 'Qualified']
        }
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    fields = fields or ['name', 'email_from', 'stage_id']
    result = Lead.read([lead_id], fields)
    return result[0] if result else {}

@mcp.tool
def get_all_stages(fields: list[str] = None, limit: int = 50) -> list[dict]:
    """
    Retrieves all available CRM pipeline stages from the Odoo system.

    This function queries the `crm.stage` model to list all defined stages in the pipeline.
    You can specify which fields to retrieve and optionally limit the number of results.

    Parameters:
    ----------
    fields : list[str], optional
        A list of field names to return for each stage.
        Defaults to ['name', 'sequence', 'fold'].
        Common fields include:
        - name: Name of the stage
        - sequence: Order in the pipeline
        - fold: Whether to fold this stage by default in Kanban

    limit : int, optional
        Maximum number of stages to return. Defaults to 50.

    Returns:
    -------
    list[dict]
        A list of dictionaries representing each stage.

    Example:
    -------
    [
        {'name': 'New', 'sequence': 1, 'fold': False},
        {'name': 'Qualified', 'sequence': 2, 'fold': False},
        ...
    ]
    """
    odoo = connect(url, database, email, password, port, protocol)
    Stage = odoo.env['crm.stage']
    fields = fields or ['name', 'sequence', 'fold']
    return Stage.search_read([], fields, limit=limit)

@mcp.tool
def get_lead_stage(lead_id: int) -> dict:
    """
    Retrieves the current stage of a given lead.

    Parameters:
    ----------
    lead_id : int
        The ID of the lead.

    Returns:
    -------
    dict
        A dictionary with the stage name, ID, sequence, and fold status.

        Example:
        {
            'id': 3,
            'name': 'Proposition',
            'sequence': 3,
            'fold': False
        }
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    result = Lead.search_read([('id', '=', lead_id)], ['stage_id'])
    if result and result[0]['stage_id']:
        stage_id, stage_name = result[0]['stage_id']
        # You can also query more fields if needed from crm.stage using stage_id
        return {'id': stage_id, 'name': stage_name}
    return {}

@mcp.tool
def set_lead_stage(lead_id: int, stage_id: int) -> dict:
    """
    Updates the stage of a given lead to a specified stage ID.

    Parameters:
    ----------
    lead_id : int
        The ID of the lead to update.
    
    stage_id : int
        The ID of the new stage to assign to the lead.

    Returns:
    -------
    dict
        A dictionary indicating whether the update was successful.

        Example:
        {
            "success": True,
            "message": "Lead stage updated successfully."
        }
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']

    success = Lead.write([lead_id], {'stage_id': stage_id})
    if success:
        return {"success": True, "message": "Lead stage updated successfully."}
    return {"success": False, "message": "Failed to update lead stage."}

@mcp.tool
def get_lost_reasons() -> list[dict]:
    """
    Fetches all possible reasons for losing a lead from the CRM.

    Returns:
    -------
    list[dict]
        A list of lost reasons, each with id and name.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Reason = odoo.env['crm.lost.reason']
    reasons = Reason.search_read([], ['id', 'name'])
    return reasons

@mcp.tool
def mark_lead_lost(lead_id: int, lost_reason_id: int = None) -> dict:
    """
    Marks a lead as lost in the CRM system.

    Parameters:
    ----------
    lead_id : int
        The ID of the lead to be marked as lost.

    lost_reason_id : int, optional
        The ID of the lost reason to associate with this lead.

    Returns:
    -------
    dict
        A dictionary indicating whether the operation was successful.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']

    data = {'active': False}
    if lost_reason_id:
        data['lost_reason'] = lost_reason_id

    success = Lead.write([lead_id], data)

    if success:
        return {"success": True, "message": "Lead marked as lost."}
    return {"success": False, "message": "Failed to mark lead as lost."}

@mcp.tool
def get_lead_details(lead_id: int) -> dict:
    """
    Retrieve detailed information about a lead from Odoo CRM.

    Parameters:
    ----------
    lead_id : int
        The unique ID of the lead.

    Returns:
    -------
    dict
        A dictionary containing the lead’s details, including:
        - name, email, phone
        - stage (name & id)
        - probability
        - type, priority
        - description
        - assigned user
        - expected revenue
        - created date, deadline
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']

    leads = Lead.read([lead_id], [
        'name', 'email_from', 'phone', 'stage_id', 'probability',
        'type', 'priority', 'user_id', 'team_id',
        'expected_revenue', 'description',
        'create_date', 'date_deadline'
    ])

    if not leads:
        return {"success": False, "message": f"Lead with id {lead_id} not found."}

    lead = leads[0]

    # Flatten relational fields
    if isinstance(lead.get('stage_id'), list):
        lead['stage_name'] = lead['stage_id'][1]
        lead['stage_id'] = lead['stage_id'][0]

    if isinstance(lead.get('user_id'), list):
        lead['user_name'] = lead['user_id'][1]
        lead['user_id'] = lead['user_id'][0]

    if isinstance(lead.get('team_id'), list):
        lead['team_name'] = lead['team_id'][1]
        lead['team_id'] = lead['team_id'][0]

    return {"success": True, "data": lead}

@mcp.tool
def convert_lead_to_opportunity(lead_id: int) -> bool:
    """
    Converts a lead into an opportunity in the CRM.

    Parameters:
    -----------
    lead_id : int
        The ID of the lead to convert.

    Returns:
    --------
    bool
        True if conversion was successful, False otherwise.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    lead = Lead.browse(lead_id)

    if not lead.exists():
        return False

    lead.write({'type': 'opportunity'})
    return True

@mcp.tool
def get_users() -> list[dict]:
    """
    Retrieves a list of active internal users (salespeople) from the CRM system.

    This tool queries the `res.users` model to get active users who are not portal/public users.
    It is useful for listing available salespeople when assigning leads or opportunities.

    Returns:
    -------
    list[dict]
        A list of user records, each represented as a dictionary containing:
        - id (int): The unique ID of the user
        - name (str): The name of the user
        - login (str): The login (email/username) of the user
    """
    odoo = connect(url, database, email, password, port, protocol)
    User = odoo.env['res.users']

    user_ids = User.search([
        ('active', '=', True),
        ('share', '=', False)  # Exclude portal/public users
    ])

    users = User.read(user_ids, ['id', 'name', 'login'])

    return users


@mcp.tool
def assign_crm_owner(
    crm_id: int,
    user_id: int | None = None,
    team_id: int | None = None,
    partner_id: int | None = None
) -> bool:
    """
    Assigns a salesperson, sales team, and/or partner to a lead or opportunity.

    Parameters:
    -----------
    crm_id : int
        ID of the lead or opportunity (both are in crm.lead).
    user_id : int, optional
        ID of the salesperson to assign.
    team_id : int, optional
        ID of the sales team to assign.
    partner_id : int, optional
        ID of the partner (customer) to link.

    Returns:
    --------
    bool
        True if assignment was successful, False otherwise.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    lead = Lead.browse(crm_id)

    if not lead.exists():
        return False

    updates = {}
    if user_id is not None:
        updates['user_id'] = user_id
    if team_id is not None:
        updates['team_id'] = team_id
    if partner_id is not None:
        updates['partner_id'] = partner_id

    if updates:
        lead.write(updates)

    return True

@mcp.tool
def get_sales_teams() -> list[dict]:
    """
    Retrieves a list of all active sales teams from the CRM system.

    This tool queries the `crm.team` model to get all active sales teams
    defined in the Odoo CRM. These teams can later be used for assigning
    ownership of leads or opportunities.

    Returns:
    -------
    list[dict]
        A list of sales team records, each represented as a dictionary containing:
        - id (int): The unique ID of the sales team
        - name (str): The name of the sales team
    """
    odoo = connect(url, database, email, password, port, protocol)
    Team = odoo.env['crm.team']

    team_ids = Team.search([('active', '=', True)])
    teams = Team.read(team_ids, ['id', 'name'])

    return teams

@mcp.tool
def get_customers() -> list[dict]:
    """
    Retrieves a list of customer records (partners) from the CRM system.

    This tool queries the `res.partner` model to get all active contacts
    that are considered customers (i.e., have either a sale or are marked
    as company/contact).

    Returns:
    -------
    list[dict]
        A list of customer records, each represented as a dictionary containing:
        - id (int): The unique ID of the customer
        - name (str): The name of the customer
        - email (str): The customer's email address
        - phone (str): The customer's phone number
    """
    odoo = connect(url, database, email, password, port, protocol)
    Partner = odoo.env['res.partner']

    customer_ids = Partner.search([
        ('active', '=', True),
        '|',
        ('is_company', '=', True),
        ('type', '=', 'contact')
    ])

    customers = Partner.read(customer_ids, ['id', 'name', 'email', 'phone'])

    return customers

@mcp.tool
def get_opportunities() -> list[dict]:
    """
    Retrieves a list of opportunity records from the CRM system.
    
    Opportunities are qualified leads that are actively being pursued
    in the sales pipeline.
    
    Returns:
    -------
    list[dict]
        A list of opportunity records, each containing:
        - id (int): The unique ID of the opportunity
        - name (str): The opportunity name/title
        - partner_id (tuple): Customer info (id, name)
        - expected_revenue (float): Expected revenue amount
        - probability (float): Probability of closing (0-100)
        - stage_id (tuple): Current stage (id, name)
        - user_id (tuple): Assigned salesperson (id, name)
        - date_deadline (str): Expected closing date
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    opportunity_ids = Lead.search([
        ('active', '=', True),
        ('type', '=', 'opportunity')
    ])
    
    opportunities = Lead.read(opportunity_ids, [
        'id', 'name', 'partner_id', 'expected_revenue', 
        'probability', 'stage_id', 'user_id', 'date_deadline'
    ])
    
    return opportunities

@mcp.tool
def get_opportunity_by_id(opportunity_id: int) -> dict:
    """
    Retrieves detailed information for a specific opportunity.
    
    Parameters:
    ----------
    opportunity_id (int): The unique ID of the opportunity
    
    Returns:
    -------
    dict: Detailed opportunity information including all fields
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    opportunity = Lead.read(opportunity_id, [
        'id', 'name', 'partner_id', 'email_from', 'phone', 
        'expected_revenue', 'probability', 'stage_id', 'user_id',
        'team_id', 'date_deadline', 'description', 'priority',
        'date_open', 'date_closed', 'won_status'
    ])
    
    return opportunity[0] if opportunity else {}

@mcp.tool
def update_opportunity(opportunity_id: int, updates: dict) -> bool:
    """
    Updates an opportunity's information in Odoo based on the given opportunity ID.

    This function uses the `crm.lead` model to perform a partial update on opportunities.
    Only the fields provided in the `updates` dictionary will be changed;
    all other fields will remain unchanged.

    Args:
        opportunity_id (int): The ID of the opportunity to update.
        updates (dict): A dictionary of fields to update. Keys must match fields in the 'crm.lead' model.

            Common updatable fields for opportunities:
            ----------------------------------------
            - name (str): Updated opportunity title or name
            - email_from (str): Updated email address
            - phone (str): Updated phone number
            - description (str): Updated notes or context
            - stage_id (int): New pipeline stage ID
            - user_id (int): New assigned user ID
            - team_id (int): New sales team ID
            - expected_revenue (float): Revised expected revenue
            - probability (float): Win probability (0-100)
            - date_deadline (str): New deadline in 'YYYY-MM-DD' format
            - priority (str): New priority level: '0', '1', '2', or '3'
            - partner_id (int): Associated customer/partner ID

            Example:
                {
                    'expected_revenue': 50000.0,
                    'probability': 75.0,
                    'stage_id': 8,
                    'description': 'Sent proposal. Awaiting decision.'
                }

    Returns:
        bool: True if the update was successful, False otherwise.

    Example:
        >>> update_opportunity(42, {'expected_revenue': 25000, 'probability': 80})
        True

    Notes:
        - You can pass only the fields you wish to update. All unspecified fields
          will remain unchanged.
        - Ensure the opportunity ID exists before calling this function to avoid errors.
        - This function targets records where type='opportunity' in the crm.lead model.
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    try:
        # Verify the opportunity exists and is actually an opportunity (not a lead)
        opportunity_data = Lead.read([opportunity_id])
        if not opportunity_data:
            raise ValueError(f"No opportunity found with ID {opportunity_id}")
        
        # Additional check to ensure it's an opportunity, not a lead
        if opportunity_data[0].get('type') != 'opportunity':
            raise ValueError(f"Record with ID {opportunity_id} is not an opportunity")
            
    except Exception:
        raise ValueError(f"Failed to retrieve opportunity with ID {opportunity_id}")

    return Lead.write([opportunity_id], updates)

@mcp.tool
def set_opportunity_stage(opportunity_id: int, stage_id: int) -> dict:
    """
    Updates the stage of a specific opportunity.
    
    Parameters:
    ----------
    opportunity_id (int): The unique ID of the opportunity
    stage_id (int): The ID of the new stage
    
    Returns:
    -------
    dict: The updated opportunity with new stage information
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    Lead.write(opportunity_id, {'stage_id': stage_id})
    
    opportunity = Lead.read(opportunity_id, [
        'id', 'name', 'stage_id', 'probability'
    ])
    
    return opportunity[0] if opportunity else {}

@mcp.tool
def mark_opportunity_won(opportunity_id: int) -> dict:
    """
    Marks an opportunity as won and moves it to the won stage.
    
    Parameters:
    ----------
    opportunity_id (int): The unique ID of the opportunity
    
    Returns:
    -------
    dict: The updated opportunity record
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    Lead.action_set_won(opportunity_id)
    
    opportunity = Lead.read(opportunity_id, [
        'id', 'name', 'stage_id', 'probability', 'date_closed'
    ])
    
    return opportunity[0] if opportunity else {}

@mcp.tool
def mark_opportunity_lost(opportunity_id: int, lost_reason_id: int = None) -> dict:
    """
    Marks an opportunity as lost with an optional reason.
    
    Parameters:
    ----------
    opportunity_id (int): The unique ID of the opportunity
    lost_reason_id (int, optional): The ID of the lost reason
    
    Returns:
    -------
    dict: The updated opportunity record
    """
    odoo = connect(url, database, email, password, port, protocol)
    Lead = odoo.env['crm.lead']
    
    update_data = {'active': False, 'probability': 0}
    if lost_reason_id:
        update_data['lost_reason'] = lost_reason_id
    
    Lead.write(opportunity_id, update_data)
    
    opportunity = Lead.read(opportunity_id, [
        'id', 'name', 'stage_id', 'probability', 'lost_reason'
    ])
    
    return opportunity[0] if opportunity else {}

@mcp.tool
def get_activities() -> list[dict]:
    """
    Retrieves a list of CRM activities (follow-ups, calls, meetings, etc.).
    
    Returns:
    -------
    list[dict]
        A list of activity records, each containing:
        - id (int): The unique ID of the activity
        - activity_type_id (tuple): Activity type (id, name)
        - summary (str): Activity summary/title
        - date_deadline (str): Due date
        - user_id (tuple): Assigned user (id, name)
        - res_model (str): Related model (crm.lead, res.partner, etc.)
        - res_id (int): Related record ID
        - state (str): Activity state (overdue, today, planned, done)
    """
    odoo = connect(url, database, email, password, port, protocol)
    Activity = odoo.env['mail.activity']
    
    activity_ids = Activity.search([
        ('res_model', 'in', ['crm.lead', 'res.partner'])
    ])
    
    activities = Activity.read(activity_ids, [
        'id', 'activity_type_id', 'summary', 'date_deadline',
        'user_id', 'res_model', 'res_id', 'state'
    ])
    
    return activities

@mcp.tool
def create_activity(res_model: str, res_id: int, activity_type_name: str, summary: str, date_deadline: str, user_id: int = None) -> dict:
    """
    Creates an activity (e.g., meeting, call, email) on a given record.
    
    Parameters:
    - odoo: An active odoorpc connection instance.
    - res_model: Model name (e.g., 'crm.lead', 'res.partner')
    - res_id: ID of the record in that model
    - activity_type_name: Type of activity (e.g., 'call', 'meeting', 'email', 'todo', 'upload document')
    - summary: Summary or title of the activity
    - date_deadline: Due date in 'YYYY-MM-DD' format
    - user_id: (Optional) ID of the user to assign the activity to
    
    Returns:
    - dict: Created activity data
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not res_id or res_id <= 0:
            raise ValueError(f"res_id must be a positive integer, got: {res_id}")
        
        # 1. Get the ID of the related model from ir.model
        model_record_id = odoo.env['ir.model'].search([('model', '=', res_model)], limit=1)
        if not model_record_id:
            raise ValueError(f"Model '{res_model}' does not exist or is not accessible.")

        # 2. Validate record existence in the target model
        target_model = odoo.env[res_model]
        if not target_model.search_count([('id', '=', res_id)]):
            raise ValueError(f"Record with ID {res_id} not found in model '{res_model}'.")

        # 3. Find activity type ID from name
        activity_type_ids = odoo.env['mail.activity.type'].search([
            ('name', 'ilike', activity_type_name.strip())
        ], limit=1)
        if not activity_type_ids:
            raise ValueError(f"Activity type '{activity_type_name}' not found.")
        activity_type_id = activity_type_ids[0]

        # 4. Validate user_id if provided
        if user_id:
            if not odoo.env['res.users'].search_count([('id', '=', user_id)]):
                raise ValueError(f"User with ID {user_id} does not exist.")

        # 5. Prepare the data for the new activity
        activity_data = {
            'res_model_id': model_record_id[0],  # CRITICAL: Use the ID from ir.model
            'res_id': int(res_id),
            'activity_type_id': activity_type_id,
            'summary': summary,
            'date_deadline': date_deadline,
        }

        if user_id:
            activity_data['user_id'] = int(user_id)
        else:
            activity_data['user_id'] = odoo.env.user.id # Assign to the current user by default

        # 6. Create the activity record
        new_activity_id = odoo.env['mail.activity'].create(activity_data)
        
        # 7. Read and return the created activity data for a clean response
        created_activity = odoo.env['mail.activity'].search_read(
            [('id', '=', new_activity_id)],
            ['id', 'summary', 'date_deadline', 'activity_type_id', 'user_id', 'res_id', 'res_model', 'res_model_id']
        )[0]
        
        return {
            'id': created_activity['id'],
            'res_id': created_activity['res_id'],
            'res_model': created_activity['res_model_id'][1], # Get the model name from the tuple
            'activity_type': created_activity['activity_type_id'][1],
            'summary': created_activity['summary'],
            'date_deadline': created_activity['date_deadline'],
            'user': created_activity['user_id'][1] if created_activity.get('user_id') else 'Unassigned'
        }
            
    except Exception as e:
        # Re-raise the exception or return a structured error, depending on your needs.
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to create activity for {res_model} ID {res_id}"
        }


@mcp.tool
def get_activity_info(activity_id: int) -> dict:
    """
    Retrieves all information for a specific Odoo activity.
    
    Parameters:
    - activity_id: The ID of the activity to retrieve.
    
    Returns:
    - dict: A dictionary containing all the details of the activity, or an error message.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError(f"activity_id must be a positive integer, got: {activity_id}")

        Activity = odoo.env['mail.activity']
        
        # Define a comprehensive list of fields to read
        fields_to_read = [
            'id', 'summary', 'note', 'date_deadline', 'state',
            'activity_type_id', 'res_id', 'res_model_id', 'res_name',
            'user_id', 'create_date', 'write_date'
        ]

        activity_records = Activity.search_read([('id', '=', activity_id)], fields_to_read)

        if not activity_records:
            raise ValueError(f"Activity with ID {activity_id} not found.")

        activity_info = activity_records[0]

        # Extract and format relevant information
        result = {
            'id': activity_info['id'],
            'summary': activity_info.get('summary', 'N/A'),
            'note': activity_info.get('note', 'N/A'),
            'date_deadline': activity_info.get('date_deadline', 'N/A'),
            'state': activity_info.get('state', 'N/A'),
            'activity_type': activity_info['activity_type_id'][1] if activity_info.get('activity_type_id') else 'N/A',
            'related_document_id': activity_info.get('res_id', 'N/A'),
            'related_document_model': activity_info['res_model_id'][1] if activity_info.get('res_model_id') else 'N/A',
            'related_document_name': activity_info.get('res_name', 'N/A'),
            'assigned_to': activity_info['user_id'][1] if activity_info.get('user_id') else 'Unassigned',
            'creation_date': activity_info.get('create_date', 'N/A'),
            'last_updated_date': activity_info.get('write_date', 'N/A')
        }

        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to retrieve activity with ID {activity_id}"
        }


@mcp.tool
def update_activity(activity_id: int, summary: str = None, date_deadline: str = None, user_id: int = None, activity_type_name: str = None, note: str = None) -> dict:
    """
    Updates an existing activity with new information. Only the fields provided will be updated.
    
    Parameters:
    - activity_id: The ID of the activity to update.
    - summary: (Optional) The new summary or title of the activity.
    - date_deadline: (Optional) The new due date in 'YYYY-MM-DD' format.
    - user_id: (Optional) The ID of the new user to assign the activity to.
    - activity_type_name: (Optional) The new type of activity (e.g., 'call', 'meeting').
    - note: (Optional) The new detailed note for the activity.
    
    Returns:
    - dict: A dictionary containing the updated details of the activity, or an error message.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError(f"activity_id must be a positive integer, got: {activity_id}")

        Activity = odoo.env['mail.activity']
        
        if not Activity.search_count([('id', '=', activity_id)]):
            raise ValueError(f"Activity with ID {activity_id} not found.")

        update_data = {}
        
        if summary is not None:
            update_data['summary'] = summary
        
        if note is not None:
            update_data['note'] = note
            
        if date_deadline is not None:
            update_data['date_deadline'] = date_deadline
            
        if user_id is not None:
            # Validate and get user ID
            if not odoo.env['res.users'].search_count([('id', '=', user_id)]):
                raise ValueError(f"User with ID {user_id} does not exist.")
            update_data['user_id'] = int(user_id)
            
        if activity_type_name is not None:
            # Validate and get activity type ID
            activity_type_ids = odoo.env['mail.activity.type'].search([
                ('name', 'ilike', activity_type_name.strip())
            ], limit=1)
            if not activity_type_ids:
                raise ValueError(f"Activity type '{activity_type_name}' not found.")
            update_data['activity_type_id'] = activity_type_ids[0]
            
        if not update_data:
            return {
                'message': f"No fields provided for update. Activity with ID {activity_id} was not changed."
            }

        Activity.write(activity_id, update_data)
        
        # Read the updated record to return the latest data
        updated_activity_info = odoo.env['mail.activity'].search_read(
            [('id', '=', activity_id)],
            ['id', 'summary', 'note', 'date_deadline', 'state', 'activity_type_id', 'res_id', 'res_model_id', 'res_name', 'user_id', 'write_date']
        )[0]
        
        return {
            'id': updated_activity_info['id'],
            'summary': updated_activity_info.get('summary', 'N/A'),
            'note': updated_activity_info.get('note', 'N/A'),
            'date_deadline': updated_activity_info.get('date_deadline', 'N/A'),
            'state': updated_activity_info.get('state', 'N/A'),
            'activity_type': updated_activity_info['activity_type_id'][1] if updated_activity_info.get('activity_type_id') else 'N/A',
            'related_document_id': updated_activity_info.get('res_id', 'N/A'),
            'related_document_model': updated_activity_info['res_model_id'][1] if updated_activity_info.get('res_model_id') else 'N/A',
            'related_document_name': updated_activity_info.get('res_name', 'N/A'),
            'assigned_to': updated_activity_info['user_id'][1] if updated_activity_info.get('user_id') else 'Unassigned',
            'last_updated_date': updated_activity_info.get('write_date', 'N/A')
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to update activity with ID {activity_id}"
        }

@mcp.tool
def get_activity_types() -> list[dict]:
    """
    Retrieves all available activity types in the system.
    
    Returns:
    -------
    list[dict]
        A list of activity types, each containing:
        - id (int): The unique ID of the activity type
        - name (str): The name of the activity type
        - category (str): The category (default, upload_file)
        - delay_count (int): Default delay in days
    """
    odoo = connect(url, database, email, password, port, protocol)
    ActivityType = odoo.env['mail.activity.type']
    
    type_ids = ActivityType.search([])
    types = ActivityType.read(type_ids, [
        'id', 'name', 'category', 'delay_count'
    ])
    
    return types


@mcp.tool
def delete_opportunity(opportunity_id: int) -> dict:
    """
    Deletes an existing opportunity.
    
    Parameters:
    - opportunity_id: The ID of the opportunity to delete.
    
    Returns:
    - dict: A success message or an error message.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(opportunity_id, int) or opportunity_id <= 0:
            raise ValueError(f"opportunity_id must be a positive integer, got: {opportunity_id}")
            
        Opportunity = odoo.env['crm.lead']
        
        if not Opportunity.search_count([('id', '=', opportunity_id)]):
            raise ValueError(f"Opportunity with ID {opportunity_id} not found.")

        Opportunity.unlink(opportunity_id)

        return {
            "success": True,
            "message": f"Opportunity with ID {opportunity_id} has been successfully deleted."
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to delete opportunity with ID {opportunity_id}"
        }


@mcp.tool
def delete_activity(activity_id: int) -> dict:
    """
    Deletes an existing activity.
    
    Parameters:
    - activity_id: The ID of the activity to delete.
    
    Returns:
    - dict: A success message or an error message.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError(f"activity_id must be a positive integer, got: {activity_id}")
            
        Activity = odoo.env['mail.activity']
        
        if not Activity.search_count([('id', '=', activity_id)]):
            raise ValueError(f"Activity with ID {activity_id} not found.")

        Activity.unlink(activity_id)

        return {
            "success": True,
            "message": f"Activity with ID {activity_id} has been successfully deleted."
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to delete activity with ID {activity_id}"
        }


@mcp.tool
def mark_activity_done(activity_id: int) -> dict:
    """
    Marks an activity as done.
    
    Parameters:
    - activity_id: The ID of the activity to mark as done.
    
    Returns:
    - dict: A success message or an error message.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError(f"activity_id must be a positive integer, got: {activity_id}")
            
        Activity = odoo.env['mail.activity']

        if not Activity.search_count([('id', '=', activity_id)]):
            raise ValueError(f"Activity with ID {activity_id} not found.")
            
        activity_record = Activity.browse(activity_id)
        # Odoo's 'mail.activity' model has an action_done method to mark it as complete.
        activity_record.action_done()

        return {
            "success": True,
            "message": f"Activity with ID {activity_id} has been marked as done."
        }
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to mark activity with ID {activity_id} as done."
        }


@mcp.tool
def get_all_activities_by_user(user_id: int) -> list:
    """
    Retrieves all activities assigned to a specific user.
    
    Parameters:
    - user_id: The ID of the user whose activities to retrieve.
    
    Returns:
    - list: A list of dictionaries, where each dictionary represents an activity.
    """
    odoo = connect(url, database, email, password, port, protocol)
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"user_id must be a positive integer, got: {user_id}")

        User = odoo.env['res.users']
        if not User.search_count([('id', '=', user_id)]):
            raise ValueError(f"User with ID {user_id} does not exist.")

        Activity = odoo.env['mail.activity']

        fields_to_read = [
            'id', 'summary', 'note', 'date_deadline', 'state',
            'activity_type_id', 'res_id', 'res_model_id', 'res_name',
            'user_id', 'create_date', 'write_date'
        ]

        activities = Activity.search_read([('user_id', '=', user_id)], fields_to_read)
        
        # Format the output to be more readable, extracting names from tuples
        formatted_activities = []
        for activity in activities:
            formatted_activities.append({
                'id': activity['id'],
                'summary': activity.get('summary', 'N/A'),
                'note': activity.get('note', 'N/A'),
                'date_deadline': activity.get('date_deadline', 'N/A'),
                'state': activity.get('state', 'N/A'),
                'activity_type': activity['activity_type_id'][1] if activity.get('activity_type_id') else 'N/A',
                'related_document_id': activity.get('res_id', 'N/A'),
                'related_document_model': activity['res_model_id'][1] if activity.get('res_model_id') else 'N/A',
                'related_document_name': activity.get('res_name', 'N/A'),
                'assigned_to': activity['user_id'][1] if activity.get('user_id') else 'Unassigned',
                'creation_date': activity.get('create_date', 'N/A'),
                'last_updated_date': activity.get('write_date', 'N/A')
            })
            
        return formatted_activities

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'error': True,
            'message': str(e),
            'details': f"Failed to retrieve activities for user with ID {user_id}"
        }


def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()