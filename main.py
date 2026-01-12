@app.route('/', methods=['POST'])
def mutate_campaigns():
    try:
        request_json = request.get_json()
        mutate_operations = request_json['mutate_operations']
        
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
