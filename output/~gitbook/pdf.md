[](https://docs.keeper.io/en/keeperpam/ "Go back to content")

[All pages](?limit=100)

[Powered by
GitBook](https://www.gitbook.com/?utm_source=content&utm_medium=trademark&utm_campaign=-MJXOXEifAmpyvNVL1to)

1 of 6

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

# Architecture

Technical details on the KeeperPAM platform architecture

##

Overview

KeeperPAM is a Zero-Knowledge platform, ensuring that encryption and
decryption of secrets, connections, and tunnels occur locally on the end
user's device through the Keeper Vault application. Access to resources in the
vault is restricted to users with explicitly assigned permissions, enabling
them to establish sessions or tunnels securely.

Keeper's zero-trust connection technology further enhances security by
providing restricted and monitored access to target systems without direct
connectivity, while never exposing underlying credentials or secrets.

This security content will cover the key areas of KeeperPAM:

  *   *   *   *   * 

Architecture Diagram

Vault Security

Router Security

Gateway Security

Connection and Tunnel Security

# Connection and Tunnel Security

Security and encryption model of Connections and Tunnels

###

Overview

KeeperPAM provides the capability to establish cloud and on-prem privileged
sessions, create tunnels, establish direct infrastructure access and secure
remote database access.

###

What is a Connection?

A Connection is a visual remote session using the web browser. Interaction
between the user and the target device is with a web browser window or within
the Keeper Desktop application.

###

What is a Tunnel?

A Tunnel is a TCP/IP connection that is established between the local vault
client through the Keeper Gateway to the target endpoint. The user can utilize
any native application for communicating with the target endpoint, such as the
command-line terminal, GUI application or database management application.

###

Connection and tunnel security

When the user establishes a connection or tunnel:

  1. The Vault Client application communicates to the Keeper Router infrastructure to initiate a WebRTC connection that is protected by a ECDH symmetric key that is stored inside the relevant Keeper record.

  2.   3. The Keeper Gateway utilizes Keeper Secrets Manager APIs to retrieve the necessary secrets from the vault, including the ECDH symmetric key.

  4. For Connections, the Vault Client (using the Apache Guacamole protocol) passes data through the WebRTC connection to the Keeper Gateway that then uses Guacd to connect to the destination found in the Keeper record.

  5. For Tunneling features (port forwarding), a local port is opened up on the local device running Keeper Desktop software. Data sent to the local port is transmitted through the WebRTC connection to the Keeper Gateway and subsequently forwarded to the target endpoint defined in the Keeper record.

  6. Session recordings of connections are protected by an AES-256 encryption key ("recording key") which is generated on the Keeper Gateway on every session. The recording key is additionally wrapped by a HKDF-derived AES-256 resource key.

The Keeper Gateway communicates with the Keeper Router through outbound-only
WebSockets. This is described in detail in the  section.

Gateway Security

# Router Security

Security and encryption model of the Keeper Router

##

Overview

Keeper Router ("Router") is a cloud service hosted in Keeper's cloud
environment which facilitates communications between the Keeper backend API,
end-user applications (Web Vault, Desktop App, etc.), and Keeper Gateways
installed in the user’s environment. The Router is responsible for
communications that perform resource discovery, password rotation, timed
access and privileged connection management.

##

How does Keeper Router work?

In traditional or legacy privileged access products, the customer is
responsible for installing on-prem software which is difficult to manage and
configure in a cloud environment. In Keeper's model, a hosted service (called
a Gateway) is installed into the customer's environment which establishes an
outbound secure connection to the Keeper Router, enabling bi-directional
communication to the Keeper cloud without any network configuration. Keeper
Router makes cloud access to on-prem infrastructure easy and secure by
utilizing WebSockets for the inbound requests.

With Keeper, WebSockets are established between the end-user device (e.g. Web
Vault) and the Keeper Router using the user's current session token. The
session token is verified by the Keeper Router to authenticate the session.
All encrypted payloads sent to the Keeper Router are wrapped by a 256-bit AES
transmission key in addition to TLS, to protect against MITM attacks. The
transmission key is generated on the end-user device and transferred to the
server using ECIES encryption via the Router's public EC key.

When a user on their Web Vault or Desktop App triggers a password rotation,
discovery job or remote connection, the message flow is the following:

  * Upon installation of the Gateway, it authenticates with the Keeper Cloud using a hashed One Time Access Token **one time**. The client signs the payload and registers a Client Device Public Key with the server on the first authentication. After the first authentication, subsequent requests are sent to the Keeper Router and signed with the Client Device Private Key.

  * The Gateway establishes an authenticated WebSocket connection using the Client Device Private Key and ECDSA signature.

  * The Vault sends a message to the Keeper Router with a command to execute (rotation, tunnel, discovery, connection) and authenticates the command using the user's active session token.

  * The Vault only transmits command and control messages, for example: `Rotate UID XXX`. No secret information is communicated between Vault and Router. The Router authenticates the command using the session token of the record's rotation configuration to validate the user's request.

  * The Router relays the command to the destination gateway through the existing WebSocket connection.

  *   * The Gateway uses Keeper Secrets Manager "update" commands to update the user's vault with any password or discovery job updates.

  * 

The Keeper Router architecture is Zero Knowledge, and Keeper's infrastructure
never has the ability to access or decrypt any of the customer's stored vault
data.

##

Keeper Router Architecture

The Router consists of two logical deployments that work together - the Head
and the Workers.

The Router is hosted in Keeper’s AWS cloud environment, isolated to each of
the global regions (US, EU, CA, AUS, JP, and US Gov).

The Head is not exposed to the internet, and performs the following functions:

  * Synchronization of global state between Workers

  * Inter-worker communication

  * Scheduling of events (e.g. rotation, discovery and connection requests)

The Workers connect to the Head via WebSocket and also use REST API calls to
retrieve information. The Workers perform the following functions:

  * Communication with Gateways

  * Communication with Keeper end-user applications

  * Communication with Keeper backend API

  * Communication with Head

Workers are scaled and load balanced in each Keeper environment. Access to the
Keeper Router is established through a common URL pattern in each region:

**US** : https://connect.keepersecurity.com

**EU** : https://connect.keepersecurity.eu

**AU** : https://connect.keepersecurity.com.au

**CA** : https://connect.keepersecurity.ca

**JP** : https://connect.keepersecurity.jp

**US GOV** : https://connect.keepersecurity.us

The end-user device will always communicate through the same Router instance.
When the end-user vault connects to the Router system, a communication
exchange is performed to ensure that the vault is communicating to the desired
gateway. Once the Gateway communication is established, a Cookie is stored
locally on the user's browser which expires automatically in 7 days. This
Cookie is only used to establish a sticky session with the target Router
instance, and does not contain any secret information.

Each Gateway device is associated with a unique UID. The Gateway UID is stored
within an encrypted “PAM Configuration” record in the administrator's vault.
This way, the Keeper vault record knows which Gateway must be used to perform
the requested rotation, discovery or connection features.

The Gateway retrieves secrets, admin credentials, record details and other
private data by using . API requests to the Keeper Cloud are sent with a
Client Device Identifier and a request body that is signed with the Client
Device Private Key. The server checks the ECDSA signature of the request for
the given Client Device Identifier using the Client Public Key of the device.
The Client Device decrypts the ciphertext response from the server with the
Application Private Key, which decrypts the Record Keys and Shared Folder
Keys. The Shared Folder Keys decrypt the Record Keys, and the Record Keys
decrypt the individual Record secrets.

After a rotation or discovery job is complete, the Gateway informs the Router
that the job is complete.  are triggered by the Router.

[Keeper Secrets Manager
APIs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[ARAM event logs](https://docs.keeper.io/en/enterprise-guide/event-reporting)

# Architecture Diagram

Keeper Password Rotation architecture diagram and data flow

##

Architecture Diagram

The KeeperPAM infrastructure and security model ensures zero-knowledge
encryption between the end-user's device and the target infrastructure.
Keeper's servers have no ability to decrypt or intercept the underlying
sessions.

###

Components

####

Keeper Gateway

The Keeper Gateway is a service which is installed into the customer's
environment and communicates outbound to Keeper services. The Gateway performs
the rotation, discovery and connections to assets on the network. The Gateway
receives commands from the Keeper Router, then uses Keeper Secrets Manager
APIs to authenticate, communicate and decrypt data from the Keeper cloud.

####

Keeper Router

The Keeper Router is infrastructure in Keeper's cloud that manages connections
between Keeper and Rotation Gateways. The Cloud Router provides real-time
messaging and communication between the Keeper Vault, customer gateway and
Keeper backend services.

####

Keeper Relay

####

Keeper Backend API

####

Scheduler

Keeper hosted infrastructure that manages timing and logistics around
scheduled rotation of credentials across the target infrastructure.

####

Admin Console and Control Plane

The Management console used to set and enforce policies across all Keeper
components.

####

Client Applications

The end-user interface for managing the vault, rotating passwords, running
discovery jobs, creating connections and managing tunnels.

###

Data Flow

  1. Keeper user performs action (rotation, connection, tunneling, discovery) from the Vault interface, Admin Console, Commander CLI or other endpoint application.

  2. Keeper Gateway establishes an outbound WebSocket connection to the Keeper Router, receives the requests to perform the action. 

  3. The Vault Client application establishes a WebRTC connection to the customer's hosted Keeper Gateway.

  4. The Keeper Gateway pulls the necessary secrets from the vault using Keeper Secrets Manager APIs.

  5. The Keeper Gateway performs the action on the target infrastructure (such as rotating a credential) and updates the relevant Keeper vault records.

  6. The Keeper Gateway runs any required privilege automation scripts on the Gateway or target machines using native protocols and APIs.

  7. Client devices securely retrieve the updated record using Keeper Secrets Manager APIs.

  8. Vault end-users receive push notifications indicating that new data is available for syncing.

  9. The vault performs encrypted syncing to the Keeper cloud to retrieve the latest record content.

  10. Keeper's Advanced Reporting & Alerts module logs all events and triggers alerts.

# Vault Security

Security and encryption model of the Keeper Vault

Keeper's platform is built with End-to-End Encryption (E2EE) across all
devices and endpoints.

  * Data stored in the platform is encrypted locally and encrypted in transit between the user's devices

  * Information exchanged between Keeper users is encrypted from vault-to-vault

  * Data at rest is encrypted with multiple layers, starting with AES-256 encryption at the record level

  * Data in transit is encrypted with TLS and additional layers of transmission encryption which protects against access MITM, service providers and untrusted networks.

A video covering this model is below.

# Gateway Security

Security and encryption model of the Keeper Gateway service

###

What is the Keeper Gateway?

##

Authentication of the Gateway

The Keeper Gateway authenticates first to the Keeper Router using the One Time
Access Token provided upon installation of the Gateway service on the target
machine. After the first authentication, subsequent API calls to the Router
authenticate using a Client Device Identifier (which is the HMAC_SHA512 hash
of the One Time Access Token).

Like any other Secrets Manager device, access can also be restricted based on
IP address in addition to the encryption and signing process.

##

How does a Gateway fetch instructions?

Rotations can be performed on-demand or on a schedule. When an on-demand
rotation, connection or discovery job is triggered by a user in the Web Vault
or Desktop App, the Keeper Router uses the active WebSocket connection to the
appropriate Gateway to receive instructions. The messages do not contain any
secret information or encrypted ciphertext. All messages sent through the
WebSocket contain only the command type (e.g. "rotate") and the affected
Record UID ("UID") which is not a secret value.

For scheduled rotations, the same mechanism is used. Rotation schedules are
tracked in the Router, and at the appropriate intervals rotation instructions
are pushed to the Gateway. When the Gateway receives a rotation task, it uses
the local KSM configuration to fetch the secrets associated with the provided
Record UIDs and decrypts the record information locally. These secrets are in
turn used to perform the rotation, discovery or connection.

##

How is the local KSM Configuration secured?

When the Gateway service is installed, the local KSM configuration is
protected by permissions on the local file system. By default, the
configuration will be stored in the home directory (`.keeper` folder) of the
user that installed the Gateway.

###

Docker Install

###

Linux Install

If Gateway is started as a user:

  * Config file: `~/.keeper/gateway-config.json`

  * Logs folder: `~/.keeper/log`

If Gateway is running as a service:

  * User: keeper-gateway-service

  * Config file: `/etc/keeper-gateway/gateway-config.json`

  * Logs folder: `/var/log/keeper-gateway`

###

Windows Install

If the Gateway is started via Command Line

  * Logs location: `C:\Users\[USER NAME]\.keeper\logs\`

  * Config File location: `C:\Users\[USER NAME]\.keeper\gateway-config.json`

If Gateway is started as a Windows Service

  * Logs location: `C:\ProgramData\KeeperGateway\`

  * Config File location: `C:\ProgramData\KeeperGatewayPrivate\`

Note: This folder can only be accessed by the user who installed the Gateway
Service.

Access to the KSM configuration file allows a user to retrieve any associated
secrets from Keeper. To prevent unauthorized access, this configuration file
is only readable by the installing user and administrative accounts. On a
Windows server, the Windows System account is used to run the service by
default, and also has access to the KSM configuration.

###

Data Caching

Caching is used for discovery but not for rotation. Every time a secret is
rotated, the Gateway retrieves associated records in real time using the
Keeper Secrets Manager APIs.

##

The Gateway Shell

The Gateway includes a virtual command shell. When the Gateway is run as a
stand-alone application, the user is dropped into the shell. When the Gateway
is run as a service, the shell is not accessible.

An SSH service is bundled with the Gateway to provide advanced debug access to
the shell. The SSH service is not running by default, and there is no way to
access the shell while it is disabled. When the Gateway service is started, an
optional argument can be supplied to enable the SSH service component. When
the SSH service is enabled, by default there are no accounts that can connect
to it. A system administrator must create a key pair with an account to
utilize SSH.

The Gateway shell does not provide commands to interact directly with secrets.

##

Commander Remote Troubleshooting

Keeper Commander can also be used to access the Gateway for troubleshooting.
This leverages the connection between the Gateway and the Router, and the
associated security mechanisms. For example, Commander can send a command to
the Router to retrieve a list of running tasks on the Gateway. These commands
can be used with any Gateway in the same enterprise as the Commander user.

##

**Secrets and Logging**

Any secrets that are retrieved during rotation are automatically scrubbed from
log messages produced by the Gateway. This includes accidental logging, such
as stack traces.

##

Post-Rotation Scripts

Keeper Gateway supports the ability to execute admin-generated scripts in
PowerShell and Bash for performing customized behaviors after a successful
rotation has taken place. The script is provided to the Gateway through a file
attachment in the corresponding Keeper record. Post-Rotation scripts are
categorized differently from general file attachments, and only the record
owner has the ability to attach post-rotation scripts on the corresponding
record.

The script is decrypted by the Gateway and then executed on the Gateway.
Connections to secondary devices, for the purpose of restarting services,
etc., must be orchestrated within the post-rotation script.

Obviously, the script which is uploaded to the Keeper record and executed on
the gateway must be protected from malicious abuse. Keeper Administrators need
to ensure that least privilege is assigned to the Keeper record.

When Post-Rotation scripts are run, stdout and stderr output from the script
are written to disk in logs. Secrets are also automatically scrubbed from this
output. Record UIDs can be logged in this way for diagnostic purposes. The
Post-Rotation script can be written with any arbitrary code, however the
Keeper Gateway provides the script with minimal information required to
perform standard use cases through the command-line parameters. This includes
the following parameters:

  * PAM Rotation Record UID (contains environment settings)

  * Resource Record UID (contains target resource data)

  * Account Record UID (the record that was rotated)

  * Old Password (from Account Record)

  * New Password (from Account Record)

  * Username (from Account Record)

After the command is executed, Keeper Gateway clears the command line history
on Linux and Windows instances.

The Keeper Relay is infrastructure in Keeper's cloud that is responsible for
establishing encrypted  connections between the end-user vault interface and
the customer-hosted Keeper Gateway service.

Keeper's Backend API is the endpoint which all Keeper client applications
communicate with. Client applications encrypt data locally and transmit
encrypted ciphertext to the API in a  format.

A full and detailed disclosure of all encryption related to data at rest, data
in transit, cloud architecture and certifications can be found on the .

The Keeper Gateway is a service that is installed on-premise in order to
execute rotation, discovery and connection tasks. The Keeper Gateway
communicates outbound to the Keeper Router using WebSockets and Keeper Secrets
Manager .

For accessing and decrypting vault records, the Keeper Gateway uses standard
Keeper Secrets Manager APIs which perform client-side encryption and
decryption of data. The  ensures least privilege and zero knowledge by
allocating only specific folders and records that can be decrypted by the
service. API requests to the Keeper Cloud are sent with a Client Device
Identifier and a request body that is signed with the Client Device Private
Key. The server checks the ECDSA signature of the request for the given Client
Device Identifier using the Client Public Key of the device.

The  passes in the configuration through an environment variable in the Docker
Compose file.

In AWS environments, the configuration can be .

If a Post-Rotation script requires access to other secrets beyond those passed
in automatically, users are strongly encouraged to use the  or the  tool.

[WebRTC](https://en.wikipedia.org/wiki/WebRTC)

[Protocol Buffer](https://en.wikipedia.org/wiki/Protocol_Buffers)

[Keeper Enterprise Encryption Model
page](https://docs.keeper.io/en/enterprise-guide/keeper-encryption-model)

Vault Encryption & Security Model

[zero-knowledge
protocols](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/security-encryption-model)

[security model of Keeper Secrets
Manager](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/security-encryption-model)

[Docker installation
method](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/getting-started/gateways/docker-installation)

[protected with the AWS
KMS](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/getting-started/gateways/advanced-configuration/gateway-configuration-
with-aws-kms)

[Keeper Secrets Manager
SDKs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[Secrets Manager CLI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/secrets-manager-command-line-interface)

KeeperPAM Architecture

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9IDMEosXrorfBpUMnr22%252Fkeeperpam-
system-
architecture.jpg%3Falt%3Dmedia%26token%3D9afb26d1-5da9-4834-8bba-2366035cc267&width=768&dpr=4&quality=100&sign=8e135273&sv=2)

