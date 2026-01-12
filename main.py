from flask import Flask, request, jsonify
from google.ads.googleads.client import GoogleAdsClient
from google.protobuf import json_format
import re

app = Flask(__name__)

@app.route('/', methods=['POST'])
def mutate_campaigns():
    try:
        request_json = request.get_json()
        mutate_operations_list = request_json['mutate_operations']
        
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
        
        # Extract customer_id by searching for ANY resource_name in the JSON
        customer_id = None
        json_str = str(mutate_operations_list)
        match = re.search(r"customers/(\d+)/", json_str)
        if match:
            customer_id = match.group(1)
        
        if not customer_id:
            return jsonify({
                "success": False, 
                "error": "Could not extract customer_id from operations"
            }), 400
        
        # Convert dict operations to protobuf MutateOperation objects
        mutate_operations = []
        for op_dict in mutate_operations_list:
            operation = client.get_type("MutateOperation")
            json_format.ParseDict(op_dict, operation._pb)
            mutate_operations.append(operation)
        
        print(f"Calling Google Ads API with {len(mutate_operations)} operations...", flush=True)
        
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=mutate_operations
        )
        
        print("SUCCESS!", flush=True)
        
        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "operations_count": len(mutate_operations),
            "results": str(response)
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

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
