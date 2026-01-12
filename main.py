from flask import Flask, request, jsonify
from google.ads.googleads.client import GoogleAdsClient

app = Flask(__name__)

@app.route('/', methods=['POST'])
def mutate_campaigns():
    try:
        request_json = request.get_json()
        mutate_operations = request_json['mutate_operations']
        
        # Make.com is double-wrapping - unwrap if needed
        if isinstance(mutate_operations, dict) and 'mutate_operations' in mutate_operations:
            mutate_operations = mutate_operations['mutate_operations']
        
        print(f"Received {len(mutate_operations)} operations")
        
        credentials = {
            "developer_token": "FFuv07GUVTShEgiFhIJuXA",
            "client_id": "64876736744-29o1ok0886up9glujb7ou1kiv8r34l7i.apps.googleusercontent.com",
            "client_secret": "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",
            "refresh_token": "1//05RQiitm33T7ZCgYIARAAGAUSNgF-L9IrVb74M5mbUJa0d3d1rtbhKyUdjXZ0frGa1kaiF73985TwCFy9ZA6jGneJ2pb7z9axWQ",
            "use_proto_plus": True,
            "login_customer_id": "2098090633"
        }
        
        client = GoogleAdsClient.load_from_dict(credentials)
        googleads_service = client.get_service("GoogleAdsService")
        
        # Extract customer_id from any operation's resource_name
        customer_id = None
        for operation in mutate_operations:
            for operation_type, operation_data in operation.items():
                if 'create' in operation_data:
                    resource_name = operation_data['create']['resource_name']
                    customer_id = resource_name.split('/')[1].replace('-', '')
                    break
            if customer_id:
                break
        
        print(f"Extracted customer_id: {customer_id}")
        print(f"Calling Google Ads API...")
        print(f"First operation: {mutate_operations[0]}")
        
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=mutate_operations
        )
        
        print(f"Success! Response received")
        
        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "operations_count": len(mutate_operations),
            "results": str(response)
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test-access', methods=['GET'])
def test_access():
    try:
        credentials = {
            "developer_token": "FFuv07GUVTShEgiFhIJuXA",
            "client_id": "64876736744-29o1ok0886up9glujb7ou1kiv8r34l7i.apps.googleusercontent.com",
            "client_secret": "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",
            "refresh_token": "1//05RQiitm33T7ZCgYIARAAGAUSNgF-L9IrVb74M5mbUJa0d3d1rtbhKyUdjXZ0frGa1kaiF73985TwCFy9ZA6jGneJ2pb7z9axWQ",
            "use_proto_plus": True
        }
        
        client = GoogleAdsClient.load_from_dict(credentials)
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        customer_ids = [c.split('/')[-1] for c in accessible_customers.resource_names]
        
        return jsonify({
            "success": True,
            "accessible_customer_ids": customer_ids,
            "count": len(customer_ids)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', methods=['POST'])
def mutate_campaigns():
    try:
        request_json = request.get_json()
        print(f"FULL REQUEST: {request_json}")
        
        mutate_operations = request_json['mutate_operations']
