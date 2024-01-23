# Create the Authorizer in API Gateway
aws apigatewayv2 create-authorizer \
    --api-id oo7qufalz8 \
    --authorizer-type REQUEST \
    --identity-source '$request.header.Authorization' \
    --name SolAssistantsAuth2 \
    --authorizer-uri 'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:215555180754:function:SolAssistantsAuthorizer/invocations' \
    --authorizer-payload-format-version '2.0' 
# Output: 

# Grant API Gateway Permission to Invoke the Lambda Authorizer
aws lambda add-permission \
    --function-name SolAssistantsAuthorizer \
    --statement-id apigateway-invoke-permissions-lambda \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:215555180754:oo7qufalz8/authorizers/pi2j78"

aws lambda add-permission \
    --function-name SolAssistantsAuthorizer \
    --statement-id apigateway-invoke-permissions-auth \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:215555180754:oo7qufalz8/*"

# Update Routes to Use the Authorizer
aws apigatewayv2 update-route \
    --api-id oo7qufalz8 \
    --route-id stc1fq9 \
    --authorization-type CUSTOM \
    --authorizer-id 7mwi06

# Redeploy the API
aws apigatewayv2 create-deployment \
    --api-id oo7qufalz8 \
    --stage-name test