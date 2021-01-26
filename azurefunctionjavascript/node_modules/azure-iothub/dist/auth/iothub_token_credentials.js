"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/*
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for
 * license information.
 */
var ms_rest_js_1 = require("@azure/ms-rest-js");
var azure_iot_common_1 = require("azure-iot-common");
/**
 * Creates shared access signatures based on the connection string passed to the constructor.
 * This class is used by the protocol layer of the SDK to add authentication headers to each request.
 */
var IoTHubTokenCredentials = /** @class */ (function () {
    function IoTHubTokenCredentials(connectionString) {
        this._connectionString = azure_iot_common_1.ConnectionString.parse(connectionString, ['HostName', 'SharedAccessKeyName', 'SharedAccessKey']);
    }
    /**
     * Adds an authorization header to the request object.
     * @param webResource The request object that needs its authorization header populated
     */
    IoTHubTokenCredentials.prototype.signRequest = function (webResource) {
        var sas = azure_iot_common_1.SharedAccessSignature.create(this._connectionString.HostName, this._connectionString.SharedAccessKeyName, this._connectionString.SharedAccessKey, azure_iot_common_1.anHourFromNow()).toString();
        webResource.headers.set(ms_rest_js_1.Constants.HeaderConstants.AUTHORIZATION, sas);
        return Promise.resolve(webResource);
    };
    /**
     * Gets the Azure IoT Hub instance name from the connection string
     */
    IoTHubTokenCredentials.prototype.getHubName = function () {
        return this._connectionString.HostName;
    };
    return IoTHubTokenCredentials;
}());
exports.IoTHubTokenCredentials = IoTHubTokenCredentials;
//# sourceMappingURL=iothub_token_credentials.js.map