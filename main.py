from flask import Flask, request, jsonify
from google.ads.googleads.client import GoogleAdsClient

app = Flask(__name__)

@app.route('/', methods=['POST'])
def mutate_campaigns():
    try:
        request_json = request.get_json()
        operations_data = request_json['operations_json']
        
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
        mutate_operations = operations_data['mutate_operations']
        
        first_resource = mutate_operations[0]['campaign_budget_operation']['create']['resource_name']
        customer_id = first_resource.split('/')[1].replace('-', '')
        
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=mutate_operations
        )
        
        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "results": str(response)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Gunicorn will handle this, no need for app.run()


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
