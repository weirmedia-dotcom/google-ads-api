from flask import Flask, request, jsonify
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import json_format
import os
import re
import json

app = Flask(__name__)

# Initialize Google Ads client
client = GoogleAdsClient.load_from_env()

def extract_customer_id(operations):
    """Extract customer_id from the first operation's resource_name."""
    if not operations or len(operations) == 0:
        return None
    
    first_op = operations[0]
    
    # Check all possible operation types
    for op_type in ['campaign_budget_operation', 'campaign_operation', 'ad_group_operation', 
                    'ad_group_criterion_operation', 'ad_group_ad_operation']:
        if op_type in first_op:
            create_obj = first_op[op_type].get('create', {})
            resource_name = create_obj.get('resource_name', '')
            
            # Extract customer ID from resource_name (e.g., "customers/2457509276/...")
            match = re.search(r'customers/(\d+)/', resource_name)
            if match:
                return match.group(1)
    
    return None

@app.route('/test-access', methods=['GET'])
def test_access():
    """Test endpoint to verify API credentials work."""
    try:
        customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID', '').replace('-', '')
        if not customer_id:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_ADS_CUSTOMER_ID not set in environment'
            }), 500
        
        googleads_service = client.get_service("GoogleAdsService")
        query = "SELECT customer.id FROM customer LIMIT 1"
        
        response = googleads_service.search(
            customer_id=customer_id,
            query=query
        )
        
        return jsonify({
            'success': True,
            'message': 'Google Ads API credentials valid',
            'customer_id': customer_id
        })
    
    except GoogleAdsException as ex:
        return jsonify({
            'success': False,
            'error': f'Google Ads API error: {str(ex)}'
        }), 500
    except Exception as ex:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(ex)}'
        }), 500

@app.route('/validate', methods=['POST'])
def validate_operations():
    """Validate operations without creating resources (validate_only=True)."""
    try:
        data = request.json
        
        # Handle mutate_operations as either string or array
        mutate_operations_data = data.get('mutate_operations')
        
        if isinstance(mutate_operations_data, str):
            # If it's a string, parse it as JSON
            try:
                mutate_operations = json.loads(mutate_operations_data)
            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False,
                    'error': f'Invalid JSON string in mutate_operations: {str(e)}'
                }), 400
        else:
            # It's already an array/list
            mutate_operations = mutate_operations_data
        
        if not mutate_operations:
            return jsonify({
                'success': False,
                'error': 'mutate_operations is required and cannot be empty'
            }), 400
        
        # Extract customer_id from operations
        customer_id = extract_customer_id(mutate_operations)
        if not customer_id:
            return jsonify({
                'success': False,
                'error': 'Could not extract customer_id from operations'
            }), 400
        
        # Get login_customer_id from environment
        login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '').replace('-', '')
        if not login_customer_id:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_ADS_LOGIN_CUSTOMER_ID not set in environment'
            }), 500
        
        # Convert JSON to protobuf messages
        protobuf_operations = []
        for op_dict in mutate_operations:
            # Create a MutateOperation protobuf message
            mutate_op = client.get_type("MutateOperation")
            json_format.ParseDict(op_dict, mutate_op)
            protobuf_operations.append(mutate_op)
        
        # Get GoogleAdsService
        googleads_service = client.get_service("GoogleAdsService")
        
        # Call mutate with validate_only=True
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=protobuf_operations,
            validate_only=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Validation successful',
            'customer_id': customer_id,
            'operations_count': len(mutate_operations)
        })
    
    except GoogleAdsException as ex:
        error_details = []
        for error in ex.failure.errors:
            error_details.append({
                'error_code': error.error_code,
                'message': error.message,
                'location': str(error.location)
            })
        
        return jsonify({
            'success': False,
            'error': 'Google Ads API validation error',
            'details': error_details,
            'request_id': ex.request_id
        }), 400
    
    except Exception as ex:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(ex)}'
        }), 500

@app.route('/', methods=['POST'])
def create_campaign():
    """Main endpoint to create campaigns via Google Ads API."""
    try:
        data = request.json
        
        # Handle mutate_operations as either string or array
        mutate_operations_data = data.get('mutate_operations')
        
        if isinstance(mutate_operations_data, str):
            # If it's a string, parse it as JSON
            try:
                mutate_operations = json.loads(mutate_operations_data)
            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False,
                    'error': f'Invalid JSON string in mutate_operations: {str(e)}'
                }), 400
        else:
            # It's already an array/list
            mutate_operations = mutate_operations_data
        
        if not mutate_operations:
            return jsonify({
                'success': False,
                'error': 'mutate_operations is required and cannot be empty'
            }), 400
        
        # Extract customer_id from operations
        customer_id = extract_customer_id(mutate_operations)
        if not customer_id:
            return jsonify({
                'success': False,
                'error': 'Could not extract customer_id from operations'
            }), 400
        
        # Get login_customer_id from environment
        login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '').replace('-', '')
        if not login_customer_id:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_ADS_LOGIN_CUSTOMER_ID not set in environment'
            }), 500
        
        # Convert JSON to protobuf messages
        protobuf_operations = []
        for op_dict in mutate_operations:
            # Create a MutateOperation protobuf message
            mutate_op = client.get_type("MutateOperation")
            json_format.ParseDict(op_dict, mutate_op)
            protobuf_operations.append(mutate_op)
        
        # Get GoogleAdsService
        googleads_service = client.get_service("GoogleAdsService")
        
        # Execute mutate operation
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=protobuf_operations
        )
        
        # Extract created resource names
        created_resources = []
        for result in response.mutate_operation_responses:
            if result.campaign_budget_result.resource_name:
                created_resources.append({
                    'type': 'campaign_budget',
                    'resource_name': result.campaign_budget_result.resource_name
                })
            elif result.campaign_result.resource_name:
                created_resources.append({
                    'type': 'campaign',
                    'resource_name': result.campaign_result.resource_name
                })
            elif result.ad_group_result.resource_name:
                created_resources.append({
                    'type': 'ad_group',
                    'resource_name': result.ad_group_result.resource_name
                })
            elif result.ad_group_criterion_result.resource_name:
                created_resources.append({
                    'type': 'ad_group_criterion',
                    'resource_name': result.ad_group_criterion_result.resource_name
                })
            elif result.ad_group_ad_result.resource_name:
                created_resources.append({
                    'type': 'ad_group_ad',
                    'resource_name': result.ad_group_ad_result.resource_name
                })
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(created_resources)} resources',
            'customer_id': customer_id,
            'created_resources': created_resources
        })
    
    except GoogleAdsException as ex:
        return jsonify({
            'success': False,
            'error': str(ex),
            'request_id': ex.request_id
        }), 400
    
    except Exception as ex:
        return jsonify({
            'success': False,
            'error': str(ex)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
