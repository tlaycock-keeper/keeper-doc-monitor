[](https://docs.keeper.io/en/keeperpam "Go back to content")

[All pages](?limit=100)

[Powered by
GitBook](https://www.gitbook.com/?utm_source=content&utm_medium=trademark&utm_campaign=-MJXOXEifAmpyvNVL1to)

1 of 40

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

Loading...

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

[Keeper Secrets Manager
APIs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[ARAM event logs](https://docs.keeper.io/en/enterprise-guide/event-reporting)

Architecture Diagram

Vault Security

Router Security

Gateway Security

Connection and Tunnel Security

[Keeper Enterprise Encryption Model
page](https://docs.keeper.io/en/enterprise-guide/keeper-encryption-model)

[zero-knowledge
protocols](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/security-encryption-model)

[security model of Keeper Secrets
Manager](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/security-encryption-model)

Docker installation method

protected with the AWS KMS

[Keeper Secrets Manager
SDKs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[Secrets Manager CLI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/secrets-manager-command-line-interface)

Vault Encryption & Security Model

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

# Getting Started

Getting Started with KeeperPAM fundamentals

##

The Basics

  *   *   *   *   *   *   *   *   *   *   *   * 

###

KeeperPAM Features

  *   *   *   *   *   *   *   * 

###

Secrets Manager Features

  *   *   * 

###

Commander CLI Features

  *   *   *   *   *   *   *   *   * 

###

Enterprise Password Manager

  * 

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

# KeeperPAM Licensing

Features included with the PAM License

##

KeeperPAM Licensing Requirements

In order to enable and use KeeperPAM, the following are required:

  *   *     * A minimum of 5 seats 

A Keeper Business or Keeper Enterprise License is required to purchase the
KeeperPAM add-on.

###

Trial License

##

Features Included with KeeperPAM

With the purchase of the Privileged Access Manager add-on, the following
features are included:

  * Secrets Manager - Unlimited API Calls

  * Password Rotation 

  * Connections

  * Tunnels

  * Remote Browser Isolation 

  * Session Recordings and Playback 

  * Discovery 

  * Keeper Connection Manager (Self-Hosted)

  * PAM Audit and Reporting

####

What is the difference between KeeperPAM and Keeper Connection Manager (Self-
Hosted)?

##

KeeperPAM License Model

The KeeperPAM add-on license includes all the advanced PAM Features. The
number of licenses for the enterprise license and the KeeperPAM license is
based on:

License Type

License Model

Business or Enterprise License

Number of Users using the Business or Enterprise Features

Privileged Access Manager Add-On

Number of Users using the Business or Enterprise Features AND PAM Features

####

Example

For example, if an organization has 100 Enterprise users and needs PAM
functionality for only 10 of them, they would purchase:

  * **100 Keeper Enterprise Licenses** for users who only need the enterprise features.

  * **10 Privileged Access Manager** **Add-Ons** , to cover the 10 users that need PAM functionality.

##

MSPs

##

Existing Customers - Updating KSM/KCM Add-Ons

For existing customers, the following existing Add-ons can be upgraded to the
Privileged Access Manager Add-On:

  * Keeper Secrets Manager Add-On

  * Keeper Connection Manager Add-On

Both the Keeper Secrets Manager and Keeper Connection Manager Add-Ons are
included as part of the Privileged Access Manager Add-On.

###

Upgrading from Keeper Secrets Manager Add-On

Upgrading to the Privileged Access Manager Add-On from the Keeper Secrets
Manager Add-On will give you:

  * Access to new KeeperPAM Features

  * Unlimited API Calls 

###

Upgrading from Keeper Connection Manager Add-On

Upgrading to the Privileged Access Manager Add-On from the Keeper Connection
Manager Add-On will give you new KeeperPAM Features which includes accessing
both the cloud and self-hosted KCM.

##

**Ready to Upgrade?**

# Enforcement Policies

Role-based enforcement policy settings for KeeperPAM

##

Overview

Role-based Access Controls (RBAC) provide your organization the ability to
define enforcements based on a user's job responsibility as well as provide
delegated administrative functions. Prior to proceeding with this guide,
familiarize yourself with roles and enforcement policies.

###

Enable PAM Policies

From the Admin Console, enable the corresponding PAM Enforcement Policies.

  * Login to the Keeper Admin Console for your region.

  * Under **Admin** > **Roles** , create a new role for PAM or modify an existing role.

  * Go to **Enforcement Policies** and open the "**Privileged Access Manager** " section.

  * 

##

Privileged Access Manager Policies

###

Secrets Manager

Policy

Definition

Commander CLI

Can create applications and manage secrets

Allow users to create and manage KSM application

###

Keeper Gateway

Policy

Definition

Commander CLI

Can create, deploy, and manage Keeper Gateways

Allow users to create, setup, and manage Keeper Gateways

###

Keeper Rotation

Policy

Definition

Commander CLI

Can configure rotation settings

Allow users to configure Rotation settings on PAM User and PAM Configuration
Record Types

Can rotate credentials

Allow users to rotate credentials on PAM User Record Types

###

Keeper Connection Manager (KCM)

Policy

Definition

Commander CLI

Can configure connection and session recording

Allow users to configure Connection and Session Recordings settings on PAM
Machine, PAM Directory, PAM Database and PAM Configuration Record Types

Can launch connections

Allow users to launch connections on PAM Machine, PAM Directory, PAM Database
Record Types

Can view session recordings

Allow users to view Session Recordings

###

Keeper Tunnels

Policy

Definition

Commander CLI

Can configure tunnel settings

Allow users to configure Tunnel settings on PAM Machine, PAM Directory, PAM
Database and PAM Configuration Record Types

Can start tunnels

Allow users to start tunnels on PAM Machine, PAM Directory, PAM Database
Record Types

###

Remote Browser Isolation (RBI)

Policy

Definition

Commander CLI

Can configure remote browsing and session recording

Allow users to configure Remote Browser and Session Recordings settings on PAM
Remote Browsing and Configuration Record Types

Can launch remote browsing

Allow users to launch remote browsing on PAM Remote Browsing Record Types

Can view RBI session recordings

Allow users to view RBI Session Recordings

###

Discovery

Discovery is currently only available on Keeper Commander. The UI is coming
soon.

Policy

Definition

Commander CLI

Can run discovery

Allow users to run discovery

###

Legacy Policies

These policies are not required moving forward, but they exist for support of
legacy features.

Policy

Definition

Commander CLI

Legacy allow rotation

Allow users to perform password rotation

###

Commander CLI

Copy

    
    
    enterprise-role ROLE_ID --enforcement "ALLOW_SECRETS_MANAGER:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_PAM_ROTATION:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_PAM_DISCOVERY:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_PAM_GATEWAY:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_CONFIGURE_ROTATION_SETTINGS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_ROTATE_CREDENTIALS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_CONFIGURE_PAM_CLOUD_CONNECTION_SETTINGS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_LAUNCH_PAM_ON_CLOUD_CONNECTION:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_CONFIGURE_PAM_TUNNELING_SETTINGS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_LAUNCH_PAM_TUNNELS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_LAUNCH_RBI:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_CONFIGURE_RBI:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_VIEW_KCM_RECORDINGS:True"
    enterprise-role ROLE_ID --enforcement "ALLOW_VIEW_RBI_RECORDINGS:True"

# Vault Structure

Understanding the Keeper Vault structure and organization for KeeperPAM

##

Overview

In a customer's environment, the Keeper Vault is deployed to all users within
the organization across all devices. The Vault is accessible through any web
browser, and also available as a native desktop application for Windows, macOS
and Linux. Accessing the Keeper vault is the foundation of the KeeperPAM
platform, since the vault is deployed to all users, enforces MFA, SSO and
implements a zero-knowledge encryption model.

When the Role-based Enforcement Policies are activated from the Keeper Admin
Console, those designated users can work with KeeperPAM functionality directly
with the vault.

  *   * 

* * *

###

Records, Record Types and Resources

In Keeper, a record can be a password, file, passkey, or any number of
possible record type templates. A record is always encrypted locally on the
user's device with a record-level encryption key. All information held within
a record is encrypted in the vault.

When working with Secrets Management and Privileged Access Management
functionality, records can also represent Applications, Machines, Directories,
Databases, Domain Controllers, Users and other infrastructure being managed.

Like any password record, these new record types can also be placed into
private or shared folders, managed directly in the vault and controlled
through policy enforcements.

* * *

###

Folders and Shared Folders

In the vault, records are placed into folders and shared folders. A typical
and recommended setup looks something like this:

  * Private Folder

    * Shared Folder containing Resources

    * Shared Folder containing User accounts

The reason that we recommend splitting up Resources and User accounts is based
on least privilege. In this configuration, the resources can be provisioned to
a user without sharing access to the underlying credentials. The user accounts
are in a separate folder and can remain private in this vault or shared to
other privileged users as required.

A resource such as a Linux machine can be seen inside the resource folder
below. The Administrative Credentials used for connecting to that resource are
linked, but not directly embedded in the resource. This way, you can provide
access to the resource without sharing the credential.

In this example, the linked Administrative Credential lives in the Users
folder with separate permissions and folder privileges.

At the Shared Folder level, both human users and applications can be assigned
with access rights. This allows least privilege enforcement across employees
and machines.

* * *

###

Application

A Secrets Manager Application is assigned to specific shared folders.
Applications are associated to devices and Gateways for accessing the assigned
records.

An Application and the associated devices and Gateways can only decrypt the
records assigned to the folder. Keeper recommends implementing the principle
of least privilege, ensuring applications are limited in their ability to
access records from the vault.

Management of Applications is found in the Keeper Secrets Manager section of
the vault. An example of an Application might be "Azure DevOps Pipeline" or
"Azure AD Rotations" as seen in the screenshot below.

For more information on Applications:

  * 

* * *

###

Device

A Device is any endpoint that needs to access secrets associated with an
Application. This can be a physical device, virtual device, or cloud-based
device. Each Client device has a unique key to read and access the secrets.

A device can be initialized through the Applications section of the vault user
interface.

For more information on Devices:

  * 

* * *

###

Gateway

The Keeper Gateway is a service that is installed on any Docker, Linux or
Windows machine in order to execute password rotation, discovery, connection,
tunneling or other privileged automation. The Gateway service can be installed
in any remote or on-prem environment, powering a secure zero-trust connection.

Typically, a Keeper Gateway is deployed to each environment that is being
managed. For example, if you are an MSP managing 500 client environments, you
may deploy 500 Keeper Gateways.

The architecture of the Keeper Gateway deployments is based on your use case
and can be reviewed with our implementation team.

  * 

* * *

###

Configuration

A PAM Configuration defines the target environment where a Keeper Gateway has
been installed. This configuration supplies important secrets to the Gateway
that can be used to manage the target infrastructure. For example, it can
contain Azure client secrets or Tenant IDs.

The PAM Configuration data is stored as a record in the vault inside the
specified "Application Folder". This way, the Gateway has the necessary
permission to retrieve this information.

We recommend defining only **one** Configuration for each Gateway.

More information about PAM Configuration records:

  * 

* * *

###

PAM Resources

Inside the vault, records define the type of resources being managed. We call
these "PAM Resources". Several new Record Types available in the vault are
associated with a resource.

When creating a resource, you can select from various targets, such as
Machine, Database, Directory, etc.

Visit the pages linked below to learn more about each PAM Resource:

PAM Record Type

Supported Assets

Windows, Linux, macOS devices, VMs, EC2 instances, Azure VMs, Network devices
and other operating systems.

MySQL, PostgreSQL, SQL Server, MongoDB, MariaDB, Oracle

Active Directory, Azure AD, OpenLDAP

Web-based Applications, self-hosted apps, cloud apps, any http or https
target.

* * *

###

PAM Users

A special record type in the Keeper Vault called PAM User can be directly
associated to any PAM Resource. The PAM User is used by the Keeper Gateway for
establishing a connection, rotating a password, discovering accounts or
running other privilege automation on a target resource.

A PAM User is linked to the PAM Resource in the "Credentials" section of the
record. This linkage ensures that access to the resource does **not** directly
allow access to the credential.

A PAM User record can be configured for on-demand and automatic rotation.

More information on PAM Users is found here:

  * 

* * *

##

Activating PAM Features

Now that you understand the basic structure of the vault, activating and
utilizing PAM features is described in the below sections.

  *   *   *   *   * 

# Applications

Secrets Manager Applications with KeeperPAM

###

What's an Application?

A Secrets Manager Application allows a machine or device to communicate with
the Keeper vault, retrieve assigned records and decrypt the data.

Folders are shared to the application, similar to how users are folders are
shared to users. This gives the application the capability of accessing and
decrypting the records in the folder.

###

Creating an Application

From the Keeper Vault, go to Secrets Manager and click on Create Application.

  * The Application Name typically represents the use case or environment where it is being used

  * The Folder selected is where the application is assigned. An application can be added to any number of shared folders.

  * Record permissions give the application either read-only or read/write access to the folder. This is an additional restriction on top of the existing shared folder permissions.

  * Click on Generate Access Token to create the first access token, representing the first device

  * If you don't plan to set up a device yet, the first access token can be discarded

###

Generating a One-Time Access Token

When creating an application, a one-time access token for the first Device is
provided. This one-time access token is supplied to the 3rd party system,
Keeper Secrets Manager SDK, Keeper Secrets Manager CLI or other device which
needs to access information from the vault.

After creating the application, it is managed from the Secrets Manager screen.
You can then assign additional devices or Keeper Gateways.

Applications can be added to new or existing Shared Folders.

Edit the Shared Folder to assign the application.

By assigning the Application to shared folders, the application's devices can
send Keeper Secrets Manager API requests to the Keeper vault to access and
manage the records assigned. There are many use cases where a device can use
Keeper Secrets Manager APIs to communicate with the Keeper vault. Below are a
few examples.

  *   *   * 

###

Assigning Gateways to Applications

Keeper Gateways are created and associated to an application. To create a new
Gateway, open the application and click on the "Gateways" tab. Select
"Provision Gateway" to create a Gateway.

Alternatively, Keeper provides a wizard that creates several components at
once, and automatically links everything together. From the main vault screen,
select "**Create New** " then "**Gateway** ".

The "Project Name" is used to create a PAM Configuration, Gateway, Application
and optionally a set of example folders and records.

# Record Linking

KeeperPAM migration of records to new linked format

##

Overview

As part of the KeeperPAM product launch, newly created resources in the Keeper
Vault—such as PAM Machines, PAM Directories, and PAM Databases—will no longer
support embedding credentials directly within the resource. Instead, KeeperPAM
now utilizes **Record Linking** , where the credential record is securely
linked to the resource. This approach ensures a clear separation of encryption
and permissions between the resource and its associated credentials.

With Record Linking, resources can be shared with users without exposing the
underlying credentials, enhancing both security and access control.

###

Conversion

For customers currently using Keeper Secrets Manager with rotation
capabilities, if a credential is embedded directly in a resource, a new
section will appear when editing the record. This section will display the
message:

**"We moved your rotating credentials down below. Please convert these
credentials into a PAM User record type."**

This update guides users to transition their rotating credentials into the
more secure **PAM User** record type for enhanced security and proper
separation of credentials from resources.

By clicking "Convert Now", you'll be asked to confirm the change and the
credentials will be separated from the resource and placed in the same folder.

Click "Next" to finish the conversion. After this is completed, a new record
in the same folder will contain the linked credential.

Once the resource has been split, PAM capabilities including connections,
tunnels and rotations can be enabled.

The Keeper Relay is infrastructure in Keeper's cloud that is responsible for
establishing encrypted  connections between the end-user vault interface and
the customer-hosted Keeper Gateway service.

Keeper's Backend API is the endpoint which all Keeper client applications
communicate with. Client applications encrypt data locally and transmit
encrypted ciphertext to the API in a  format.

The Keeper Gateway communicates with the Keeper Router through outbound-only
WebSockets. This is described in detail in the  section.

or  License

If you are not a Keeper customer or do not have the required license, you can
start a free . The enterprise trial will also **include** the Privileged
Access Manager Add-on.

KeeperPAM is a cloud-native privileged access solution that requires only a
lightweight gateway installation, while Keeper Connection Manager (KCM) is a
fully self-hosted solution. For more information, visit this .

Keeper’s  allows MSPs and their Managed Companies (MCs) to allocate Keeper
licenses to their users and pay only for used licenses at the beginning of the
following month.

KeeperPAM will be a  that MSPs can add or remove at any time for their Managed
Companies.

Features available with the KeeperPAM Add-On are listed .

To purchase, upgrade, or if you have any questions, contact your Keeper
account manager or use our .

Enable all the  to use the new features.

The  CLI `enterprise-role` command can be used to set these policies through
automation. The list of policies related to PAM functionality is listed below.

The fastest way to understand the relationship between records, folders,
applications and configurations is using the . This wizard instantly creates a
sandbox environment where you can work with the different resources and vault
records.

Copy

    
    
    ALLOW_SECRETS_MANAGER

Copy

    
    
    ALLOW_PAM_GATEWAY

Copy

    
    
    ALLOW_CONFIGURE_ROTATION_SETTINGS

Copy

    
    
    ALLOW_ROTATE_CREDENTIALS

Copy

    
    
    ALLOW_CONFIGURE_PAM_CLOUD_CONNECTION_SETTINGS

Copy

    
    
    ALLOW_LAUNCH_PAM_ON_CLOUD_CONNECTION

Copy

    
    
    ALLOW_VIEW_KCM_RECORDINGS

Copy

    
    
    ALLOW_CONFIGURE_PAM_TUNNELING_SETTINGS

Copy

    
    
    ALLOW_LAUNCH_PAM_TUNNELS

Copy

    
    
    ALLOW_CONFIGURE_RBI

Copy

    
    
    ALLOW_LAUNCH_RBI

Copy

    
    
    ALLOW_VIEW_RBI_RECORDINGS

Copy

    
    
    ALLOW_PAM_DISCOVERY

Copy

    
    
    ALLOW_PAM_ROTATION

[WebRTC](https://en.wikipedia.org/wiki/WebRTC)

[Protocol Buffer](https://en.wikipedia.org/wiki/Protocol_Buffers)

Architecture

Licensing

Enforcement policies

Vault structure

Record Linking

Applications

Devices

Gateways

PAM Configuration

PAM Resources

PAM Users

Sharing and Access Control

[Password Rotation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/password-rotation)

[Connections](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/connections)

[Tunnels](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/tunnels)

[Remote Browser Isolation
(RBI)](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[Session Recording &
Playback](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/session-recording-and-playback)

[SSH Agent](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/ssh-agent)

[Discovery](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/discovery)

[On-Prem Connection
Manager](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/on-prem-connection-manager)

[Secrets Manager CLI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/secrets-manager-command-line-interface)

[Developer SDKs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[Integrations](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/integrations)

[Import and Export](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/import-and-export-commands/import-export-commands)

[Reporting](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/reporting-commands)

[Enterprise
Management](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/enterprise-management-commands)

[Record Management](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/record-commands)

[Sharing](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/sharing-commands)

[KeeperPAM Commands](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/keeperpam-commands)

[Secrets Management
Commands](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/secrets-manager-commands)

[MSP Management
Commands](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/msp-management-commands)

[Miscellaneous
Commands](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/misc-commands)

[Enterprise Admin Guide](https://docs.keeper.io/en/enterprise-guide)

Gateway Security

[Keeper Business](https://www.keepersecurity.com/business.html)

[Keeper Enterprise](https://www.keepersecurity.com/enterprise.html)

[Privileged Access Manager Add-On](https://www.keepersecurity.com/privileged-
access-management/)

[enterprise license trial](https://www.keepersecurity.com/start-business-
trial.html)

[online form](https://www.keepersecurity.com/contact.html?t=b&r=sales)

PAM enforcement policies

[Keeper Commander](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/overview)

[Accessing the KeeperPAM Console and
Vault](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/setup-steps)

Activating Enforcement Policies

[Quick Start
Wizard](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/quick-start-sandbox)

Applications

Devices

Gateways

PAM Configuration

PAM Users

[Password Rotation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/password-rotation)

[Connections](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/connections)

[Tunnels](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/tunnels)

[Remote Browser
Isolation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[Discovery](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/discovery)

PAM Machine

PAM Database

PAM Directory

PAM Remote Browser

[Secrets Manager CLI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/secrets-manager-command-line-interface)

[Developer SDKs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[Integrations](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/integrations)

here

# Gateways

Installation and setup of the Keeper Gateway

##

Overview

The Keeper Gateway is a service that is installed on any Docker, Linux or
Windows machine in order to execute rotation, discovery, connection and
tunneling. A single Gateway can be used to communicate with any target
infrastructure, both on-prem and cloud. Typically, customers deploy a Keeper
Gateway in each environment that is being managed.

###

**Platforms Supported**

  *   *   * 

###

Platform Specific Capabilities

The Keeper Gateway offers different feature capabilities based on the
underlying operating system and hardware. We recommend using Docker on a Linux
or Windows host with x86 CPUs for full feature support and ease of management.

Platform

Compatibility

**Docker** (Linux or Windows host w/ x86)

  * All features supported

**Linux** (RHEL 8, Rocky Linux 8)

  * All features supported

**Docker** (Linux host on ARM)

  * No Remote Browser Isolation

**Linux** **Binary Install** (Ubuntu, Debian)

  * No Remote Browser Isolation

  * Limited connection protocols

**Windows Binary Install**

  * No Remote Browser Isolation

  * No database connections

Note: EL9 which includes Rocky Linux 9 and RHEL 9 support is coming soon.

###

System Requirements

System requirements vary based on the number of simultaneous user sessions and
the types of connections being established. As the volume of simultaneous
connections grows, scaling CPU and memory resources becomes essential. In
particular, remote browser isolation (RBI) launches a headless Chromium
instance for each session. If you anticipate a high number of RBI sessions,
ensure the system is scaled to meet these demands.

For a testing or sandbox a minimum of 2 CPUs with 8GB of memory and 10GB of
storage is required. In a production environment, increase to at least 4 CPUs
with 16GB of memory. Scale the number of CPUs and memory as the number of
simultaneous sessions increases.

##

Installation Steps

The Keeper Gateway generates encryption keys and a local Secrets Manager
configuration that is used to authenticate with the Keeper cloud. The location
depends on the context in which the Gateway is being run. It can be installed
to the local user or installed as a service.

  * Login to the **Keeper Web Vault** or **Desktop App**(version 17.1 or newer required)

  * Click on **Secrets Manager** on the left side

  * Create a new Secrets Manager Application or select existing application

  * Click on the "**Gateways** " tab and click "**Provision Gateway** "

  * Select Docker, Linux or Windows install method

  * Install the Keeper Gateway using the provided method

During the creating of a Keeper Gateway using a one-time token method for
Linux and Windows, you have the choice to select "Lock external WAN IP Address
of device for initial request". This will additionally IP lock the Gateway in
addition to the authentication and encryption built into the service.

Based on your Operating System, refer to the corresponding guide on installing
the Keeper Gateway:

  *   *   * 

####

Additional Installation Configurations

# Devices

Keeper Secrets Manager Devices with KeeperPAM

###

What's a Device?

A Device can be any machine, application or endpoint that has the ability to
communicate with the Keeper platform, authenticate and decrypt data that has
been provisioned.

Applications have any number of devices associated. Each device has a unique
identifier so that it can be tightly controlled and managed. Devices
authenticate and decrypt data using a API and encryption model as defined in
the Keeper Secrets Manager Security & Encryption model page.

  * 

###

Creating a Device

A device can be created through the Applications section of the vault user
interface or through the Keeper Commander CLI.

From the Vault user interface, go to Secrets Manager and select the
Application. Then select the Devices tab and click "Add Device".

###

Device Initialization

A Keeper device can be initialized through either a One-Time Access Token or a
pre-built configuration file in either base64 or JSON format.

####

One-Time Access Token Initialization

The One-Time Access Token is an encryption key used by a device for only one
authentication to the cloud. After that, a local configuration is created with
all of the necessary keys for subsequent authentications and decryption of the
resulting vault ciphertext. The Keeper Secrets Manager SDKs and many out of
the box integrations utilize this method.

One additional feature of this method is that you can optionally lock down API
requests to a specific IP address. The IP address allowed to transact is based
on the IP as seen by Keeper's cloud infrastructure.

  * 

####

Configuration File Initialization

The Configuration file method of creating a device is useful for tools and
integrations where all of the secrets need to be provided at runtime. Most of
the CI/CD integration methods use this pre-built configuration file.

For more information about the contents of a Keeper Secrets Manager
configuration:

  * 

####

Commander CLI

The Keeper Commander CLI can create devices with some additional capabilities
that are not available in the UI. For example, the CLI can create any number
of devices in bulk, or set an expiration on the validity of the device.

Additional features of the Commander CLI device initialization method:

  * Control over the device name

  * Access expiration when the device can be initialized

  * Access expiration of the device 

  * Allow all IPs or restrict to the first requested IP

  * Generate a number of device tokens or configurations in bulk

  * Option to initialize with a on-time access token or configuration file

####

Command Help

secrets-manager client add --app [APP NAME OR UID] --unlock-ip

Options:

**\--name** [CLIENT NAME] : Name of the client (Default: Random 10 characters
string)

**\--first-access-expires-in-min** [MIN] : First time access expiration
(Default 60, Max 1440)

**\--access-expire-in-min** [MIN] : Client access expiration (Default: no
expiration)

**\--unlock-ip** : Does not lock IP address to first requesting device

**\--count** [NUM] : Number of tokens to generate (Default: 1)

**\--config-init** [json, b64 or k8s] : Initialize configuration string from a
one-time token

Example:

Copy

    
    
    secrets-manager client add --app "My Infrastructure App" --unlock-ip

  * 

# Docker Installation

Instructions for installing Keeper Gateway on Docker

##

Overview

For full PAM capabilities, use a **Linux host with a x86 AMD processor**.

###

Prerequisites

  * A Linux host with a x86 AMD processor

  * 

Note: The syntax is `docker-compose` for servers, but on a local Docker
Desktop it might be `docker compose` (with no space).

###

Create a Gateway

A new Gateway deployment can be created by clicking on **Create New** >
**Gateway** from the Web Vault or Desktop App (version 17.1 or newer
required).

You can also create a Gateway and configuration file from the Commander CLI:

Copy

    
    
    pam gateway new -n "<Gateway Name>" -a <Application Name or UID> -c b64

The Application names and UIDs can be found with `secrets-manager app list`

###

Installation

1

###

Docker Compose

A Docker Compose file is provided through the Vault UI. Typically this file
would be saved in your local environment as `docker-compose.yml` in your
preferred folder. An example is below:

Copy

    
    
    services:
          keeper-gateway:
            platform: linux/amd64
            image: keeper/gateway:latest
            shm_size: 2g
            security_opt:
              - "seccomp:docker-seccomp.json"
            environment:
              ACCEPT_EULA: Y
              GATEWAY_CONFIG: XXXXXXXXXXXXXXXXX

The only required environment variable setting is GATEWAY_CONFIG which is the
resulting base64-encoded configuration provided when creating a Gateway
device.

2

###

SecComp File

Download this file called `docker-seccomp.json` and place it in the same
folder as your Docker Compose file.

3

###

Start the Service

Ensure that you are located in the folder where the `docker-compose.yml` is
saved. Executing the following command will run the Keeper Gateway container
in the background, as specified in the docker compose file:

Copy

    
    
    docker compose up -d

###

**Logging**

When running the latest version of the Keeper Gateway, you'll see the output
in the logs like below:

Copy

    
    
    docker compose logs keeper-gateway

On the Vault UI in the **Secrets Manager** > **Applications** > **Gateways**
screen, the Gateway will show Online.

###

Gateway Service Management

####

Starting the service

Copy

    
    
    docker compose up -d

####

Stopping the service

Copy

    
    
    docker compose stop

####

Restarting the service

Copy

    
    
    docker compose restart

####

Connecting to the Gateway container

Copy

    
    
    docker compose exec keeper-gateway bash

###

Enable Debugging

If you need to enable verbose debug logs on the Gateway, enable debug logging
by adding the below `environment` section variables to your Docker Compose
file:

Copy

    
    
    services:
          keeper-gateway:
            .....
            environment:
              KEEPER_GATEWAY_LOG_LEVEL: "debug" # logs for gateway
              LOG_LEVEL: "debug" # logs for guacd

After debug is enabled, restart the service with `docker compose restart`

####

Tailing the logs:

Copy

    
    
    docker compose logs -f keeper-gateway

###

**Updating**

Executing the following command will update the Keeper Gateway container to
the latest version and restart the service:

Copy

    
    
    docker compose pull
    docker compose down
    docker compose up -d

###

Start up automatically

Adding the "restart" parameter in the `docker-compose.yml` file will assign a
restart policy to the environment:

Copy

    
    
    restart: always

###

Starting Gateway on Reboot

If you would like to force the host operating system to automatically start
the Keeper Gateway on a Docker installation, follow these steps (Linux host).

First, create a `.service` file in `/etc/systemd/system/keeper-
gateway.service`

Copy

    
    
    [Unit]
    Description=Keeper Gateway Docker Compose
    Requires=docker.service
    After=docker.service
    
    [Service]
    Type=oneshot
    RemainAfterExit=yes
    WorkingDirectory=/home/ec2-user
    ExecStart=/usr/local/bin/docker-compose up -d
    ExecStop=/usr/local/bin/docker-compose down
    User=ec2-user
    Group=docker
    
    [Install]
    WantedBy=multi-user.target

NOTE:

  * Replace `/home/ec2-user` with the path to your docker-compose.yml

  * Replace `ec2-user` user with your user running Docker

  * Replace `docker` group with your defined group

Then enable the service:

Copy

    
    
    sudo systemctl daemon-reload
    sudo systemctl enable keeper-gateway.service
    sudo systemctl start keeper-gateway.service

###

References:

  *   * 

# Creating a Gateway

Creating a Keeper Gateway

##

Overview

In order to install and setup a Keeper Gateway device, you need to have a few
resources set up:

  * Shared Folders to hold the PAM Resources (Machines, Databases, Users, etc)

  * Keeper Secrets Manager application

  * PAM Configuration

To simplify the process, we have a new Gateway wizard which creates all of the
necessary components. Or, you can run each step individually.

##

Using the Gateway Wizard

The fastest way to create a Gateway and associated resources is using the
Gateway Wizard. From the Web Vault or Desktop App, click on **Create New** >
**Gateway.**

The below link describes how to create a sandbox environment in just a few
steps:

  * 

##

Using Keeper Secrets Manager

To set up a Keeper Gateway manually using the Keeper Secrets Manager
application resources, follow these steps.

1

###

Create a Secrets Manager Application

  * In the Keeper Web Vault or Desktop App user interface, create a Shared Folder. This Shared Folder will contain the PAM resource records.

  * Navigate to the "Secret Managers" tab on the left and click on "Create Application" to create a KSM application

  * In the prompted window:

    * Enter the name of your KSM application

    * Choose the Shared Folder

    * Set the Record Permissions for Application to "Can Edit"

    * Click on "Generate Access Token" and then click on "OK"

    * You can safely ignore the first One-Time Access Token generated for the newly created KSM application. When creating a Keeper Gateway device, a different One-Time Access Token will be created.

2

##

Generate the Gateway Token

  * From the Application screen, open the **Gateways** tab

  * Click on **Provision Gateway**

  * Select a name for the Gateway and the operating system

  * Follow the on-screen instructions based on the type of install

##

Using Commander CLI

You can also create a Gateway and configuration file from the Commander CLI.
The below CLI commands will create a Secrets Manager application, shared
folders and other resources before creating a Gateway instance.

####

Create an Application

Copy

    
    
    secrets-manager app create "My Infrastructure"

####

Create Folders

Copy

    
    
    mkdir -uf "My Infrastructure"
    mkdir -sf -a "My Infrastructure/Resources"
    mkdir -sf -a "My Infrastructure/Users"

####

Share the KSM app to the Shared Folders

Copy

    
    
    secrets-manager share add --app "My Infrastructure" --secret <Resources folder UID>
    secrets-manager share add --app "My Infrastructure" --secret <Users folder UID>

####

Create a Gateway

Copy

    
    
    pam gateway new -n "My Demo Gateway" -a "My Infrastructure"

Copy

    
    
    pam gateway new -n "My Demo Gateway" -a "My Infrastructure" -c b64

# Linux Installation

Instructions for installing Keeper Gateway on Linux

##

Overview

This document contains information on how to install, configure, and update
your Keeper Gateway on Linux.

##

Prerequisites

  *   * For full capabilities, use Rocky Linux 8, RHEL 8 or Alma Linux 8.

  * 

##

Installation

####

**Install Command**

Executing the following command will install the Keeper Gateway, and run it as
a service:

Copy

    
    
    curl -fsSL https://keepersecurity.com/pam/install | \
      sudo bash -s -- --token XXXXXX

  * Replace XXXXX with the One-Time Access Token provided from creating the Keeper Gateway

####

**Installation Location**

The gateway will be installed in the following location:

Copy

    
    
    /usr/local/bin/keeper-gateway

An alias `gateway` is also created in the same directory

Copy

    
    
    gateway -> /usr/local/bin/keeper-gateway

##

Gateway Service Management

For managing the Keeper Gateway as a service, the following are created during
the Gateway installation:

  * A `keeper-gateway `folder

  * A `keeper-gw` user

**keeper-gateway folder**

The `keeper-gateway` folder contains the gateway configuration file and is
created in the following location:

Copy

    
    
    /etc/keeper-gateway

**keeper-gw user**

During the gateway installation, a new user, `keeper-gw`, is created and added
to the sudoers list in `/etc/sudoers.d/.`

The `keeper-gw` user is the owner of the keeper-gateway folder and runs the
gateway service. This is required when performing rotations on the gateway
service and performing post-execution scripts.

###

Managing the Gateway Service

The following commands can be executed to start, restart, or stop the Keeper
Gateway as a service:

Copy

    
    
    sudo systemctl start keeper-gateway
    sudo systemctl restart keeper-gateway
    sudo systemctl stop keeper-gateway

##

**Keeper Gateway Configuration File**

If the Keeper Gateway is installed and running as a service, the gateway
configuration file is stored in the following location:

Copy

    
    
    /etc/keeper-gateway/gateway-config.json

If the Keeper Gateway is installed locally and not running as a service, the
gateway configuration file is stored in the following location:

Copy

    
    
    <User>/.keeper/gateway-config.json

##

**Keeper Gateway Log files**

Logs that contain helpful debugging information are automatically created and
stored on the local machine.

If the Gateway is running as a service, the log files are stored in the
following location:

Copy

    
    
    /var/log/keeper-gateway/

If the Gateway is not running as a service, the log files are stored in the
following location:

Copy

    
    
    <User>/.keeper/logs/

###

**Verbose Logging**

To add verbose debug logging, modify this file:

Copy

    
    
    /etc/systemd/system/keeper-gateway.service

and add the `-d` flag to the "gateway start" command, e.g:

Copy

    
    
    ExecStart=/bin/bash -c "/usr/local/bin/gateway start --service -d --config-file /etc/keeper-gateway/gateway-config.json"

Apply changes to the service:

Copy

    
    
    sudo systemctl daemon-reload
    sudo systemctl restart keeper-gateway

**Tailing the Logs**

Copy

    
    
    sudo journalctl -u keeper-gateway.service -f

##

**Upgrading**

Executing the following command will upgrade the Keeper Gateway to the latest
version:

Copy

    
    
    curl -fsSL https://keepersecurity.com/pam/install | sudo bash -s --

##

**Auto Update**

Configure your Keeper Gateway installation to automatically check for updates,
ensuring it stays up-to-date with the latest version.

  * 

##

**Uninstalling**

Executing the following command will uninstall the Keeper Gateway:

Copy

    
    
    curl -fsSL https://keepersecurity.com/pam/uninstall | sudo bash -s --

# Windows Installation

Instructions for installing Keeper Gateway on Windows

##

Overview

This document contains information on how to install, configure, and update
the Keeper Gateway on Windows.

###

Prerequisite

###

Installation

The latest Keeper Gateway for Windows is downloaded from here:

  * 

You can run the service under system privilege or use a service account.

####

New Installs

####

Upgrading

If you are upgrading an existing Gateway, un-check the "Enter a Keeper One-
Time Access Token" so that the existing configuration is maintained.

####

**Installation Location**

The default installation location is the following:

Copy

    
    
    C:\ProgramFiles (x86)\Keeper Gateway\<version>

####

Setup Options

  * Install Windows service - Installs the gateway as a Windows service.

    *     * Start Windows service - Start the Keeper Gateway service immediately after installation

    * Enable automatic updates

  *   * Remove Keeper Gateway configuration and logs from previous installations

####

Specifying the Keeper Gateway Service Account

If "Use service account" is specified you will be prompted to enter the valid
credentials of the desired service account:

####

One-Time Access Token

After clicking "Next", click "Install" in the next screen to install the
Keeper Gateway.

###

Gateway Service Management

After installing and running the Keeper Gateway as a service, this service can
be accessed and easily managed within the Windows Services Manager as "Keeper
Gateway Service".

###

**Configuration File**

If the Keeper Gateway is installed and running as a service, the gateway
configuration file is stored in the following location:

Copy

    
    
    C:\ProgramData\KeeperGateway\config\gateway-config.json

If the Keeper Gateway is installed locally and not running as a service, the
gateway configuration file is stored in the following location:

Copy

    
    
    C:\Users\<User>\.keeper\gateway-config.json

###

**Log files**

Logs that contain helpful debugging information are automatically created and
stored on the local machine.

If the gateway is running as a service, the gateway log files are stored in
the following location:

Copy

    
    
    C:\ProgramData\KeeperGateway\logs\

If the gateway is not running as a service, the gateway log files are stored
in the following location:

Copy

    
    
    C:\Users\<User>\.keeper\logs\

####

**Verbose Logging**

To activate verbose logging:

  * Go to Windows Services > Keeper Gateway > Properties

  * Stop the service

  * Set the "Start parameters" to: `--debug` or `-d`

  * Start the service by clicking on "Start" _Do not click "OK" without first starting the service as it will not persist the Parameter setting_

###

**Upgrading**

To upgrade, stop the service, install the latest version and then start the
service.

  * Back up your `gateway-config.json` configuration file

  * Run the latest Keeper Gateway installer

  * During installation **DO NOT** select "Enter a Keeper One-Time Access Token".

###

**Auto Updates**

Select "Enable automatic updates" during the installer process to ensure that
your Keeper Gateway is automatically updated when there are new versions
available.

* * *

###

Silent Install

This section provides instructions for performing a silent installation of the
Keeper Gateway on Windows systems. Silent installation allows the setup
process to run in the background without displaying any user interface or
messages.

To install the Keeper Gateway silently, use the following command in your
command prompt or script:

Copy

    
    
    keeper-gateway_windows_x86_64.exe /verysilent /suppressmsgboxes /norestart /token=<TOKEN>

Replace `<TOKEN>` with the token provided in the Keeper Vault when creating
the Keeper Gateway.

####

Configuration Options

If you have previously installed Keeper Gateway and wish to use the existing
configuration, you can bypass the token entry by using:

Copy

    
    
    /existingconfig=1

To generate a log file during the installation process, use the following
option and specify the desired log file path:

Copy

    
    
    /log=<Optional log file>

####

**Windows Service Account**

If you prefer to run the Keeper Gateway under a specific Windows service
account, use the following options to specify the account details:

Copy

    
    
    /mergetasks="service/account" /serviceuser=<ACCOUNT USERNAME> /servicepass=<ACCOUNT PASSWORD>

Replace `<ACCOUNT USERNAME>` and `<ACCOUNT PASSWORD>` with the credentials of
the service account you intend to use.

####

**Auto Updater**

To enable the Auto Updater feature, allowing Keeper Gateway to automatically
check for and apply updates, use the following option:

Copy

    
    
    /autoupdate=1

###

Uninstalling

To uninstall the service:

  * Uninstall Keeper Gateway from "Add and remove programs"

  * If desired, delete the private configuration .json file

# Advanced Configuration

Advanced Keeper Gateway Configurations

##

Overview

This section will cover additional configurations to modify the Keeper
Gateway's default behavior.

##

Support Configurations

The following are supported configurations for the Keeper Gateway:

  *   * 

# Gateway Configuration with AWS KMS

Storing and protecting the Keeper Gateway Configuration using AWS KMS

##

**Overview**

If the Keeper Gateway is installed on an AWS EC2 Instance, the corresponding
Gateway configuration file can be protected and stored in AWS Secrets Manager.
This method eliminates the need for storing a configuration file on the
instance, and instead stores the configuration file with AWS KMS protection.

###

**AWS Key Management Service (KMS) Key**

AWS KMS is a fully managed service that makes it easy for you to create and
control the cryptographic keys used to encrypt and decrypt your data. The
service is integrated with other AWS services, making it easier to encrypt
data and manage keys. You will need a AWS KMS key as part of this process, and
it is recommended that you follow the principle of least privilege when
assigning permissions to this key.

###

Prerequisites

In order to use AWS KMS to protect the Gateway configuration secrets, you need
to install the Keeper Gateway on an EC2 instance which assumes an IAM Role.
This works on either Docker or Linux install methods.

  *   * 

###

Generate a Configuration

From the Keeper Vault, go to **Secrets Manager** > **Applications** and select
the application configured with your Gateway. Then select the Gateways tab and
select "Provision Gateway".

Select the Gateway initialization method of "Configuration" and click Next.

Alternatively, you can generate a One-Time Access Token and then use the
Keeper Gateway's "gateway ott-init" command:

Copy

    
    
    gateway ott-init [ONE-TIME-TOKEN]

In either case, you'll be provided with a base64 encoded configuration. Save
this for the next step.

###

Create Secret in AWS Secrets Manager

From the AWS Console, go to the Secrets Manager and create a new secret.

  * Select "Other type of secret"

  * Select Plaintext and paste the entire base64 value there.

  * Click **Next**.

Enter a **Secret Name** and a description then click **Next** , **Next** and
**Store**.

###

Assign Policy to Instance Role

The EC2 instance role needs to be assigned a policy which provides read access
to the specific AWS Secrets Manager key. As an example:

Copy

    
    
    {
        "Sid": "SecretsManagerPermissions",
        "Effect": "Allow",
        "Action": [
            "secretsmanager:GetSecretValue"
         ],
         "Resource": "arn:aws:secretsmanager:us-west-1:XXX:secret:XXX"
    }

###

Confirming Access

From the EC2 instance, the below command will confirm the policy has been
applied:

Copy

    
    
    aws secretsmanager get-secret-value --secret-id YourSecretName --query SecretString --output text

###

Configuration of the Keeper Gateway

####

Docker Install Method

For Docker installations, remove the `GATEWAY_CONFIG` entry and add
`AWS_KMS_SECRET_NAME` with the value containing the name of the secret from
the AWS secrets manager.

Copy

    
    
    services:
          keeper-gateway:
            platform: linux/amd64
            image: keeper/gateway:latest
            shm_size: 2g
            security_opt:
              - "seccomp:docker-seccomp.json"
            environment:
              ACCEPT_EULA: Y
              AWS_KMS_SECRET_NAME: "YourSecretName"

Then update the service with the new environment:

Copy

    
    
    docker compose pull
    docker compose down
    docker compose up -d

####

Linux Install Method

Open the Keeper Gateway service unit file:

`/etc/systemd/system/keeper-gateway.service`

Modify the "ExecStart" line as seen below, replacing YourSecretName with your
assigned name.

Copy

    
    
    ExecStart=/bin/bash -c "/usr/local/bin/gateway start --service --aws-kms-secret-name="YourSecretName" --log-to-stdout"

Apply changes to the service:

Copy

    
    
    sudo systemctl daemon-reload
    sudo systemctl restart keeper-gateway

If there are any errors starting up, they can be seen through this command:

Copy

    
    
    systemctl status keeper-gateway.service

# Alerts and SIEM Integration

Monitoring Gateway events and integrating with your SIEM

###

Overview

KeeperPAM supports integration with your SIEM provider to provide real-time
event logging and monitoring of all privileged access management activity. In
the Keeper Admin Console, alerts can also be configured based on any event.

For more information on activating SIEM integration from the Keeper Enterprise
guide:

  * 

###

Features

  * Push over 200 different event types to any connected SIEM provider

  * Send alerts to email, SMS, Webhook, Slack or Microsoft Teams on any event trigger

  * 

###

KeeperPAM Events

Events related to KeeperPAM include:

  * Starting and stopping sessions, tunnels, remote browser isolation

  * Gateway lifecycle (online, offline, added/removed)

  * Connection lifecycle (creation, editing and deleting PAM resources)

###

Recommended Alerts

As a KeeperPAM administrator, it is useful to receive alerts related to
Gateway actions, such as when a Gateway goes offline (in case of server outage
or system restart).

From the Admin Console, go to Reporting & Alerts > Alerts > select Event Types
and set the recipient information.

Event alert details will include the name and UID of the affected Keeper
gateway.

Email alerts contain event information

# Auto Updater

Instructions for installing and configuring the Auto Updater for the Keeper
Gateway.

##

Overview

Automatic updates of the Keeper Gateway can be enabled on Linux and Windows
installations through Keeper's Auto Updater feature. The Auto Updater makes
periodic checks to update your Keeper Gateway to the latest version.

By default, the Auto Updater is disabled when installing the Keeper Gateway

We recommend enabling the Auto Updater to ensure you receive the most recent
security and functionality enhancements. The Auto Updater verifies all Keeper
Gateway downloads by checking the GPG signature of hash value, which are then
utilized to checksum each file.

##

**Auto Updater Installation**

###

**Prerequisites**

  * Ensure that you have administrative privileges on the system.

  * Version 1.4.0 or later of Keeper Gateway is required.

###

**Docker**

On Docker based installations, the best way to update the container is running
the below commands from a cron job or your CI/CD tools.

As an example, create a file called `update_gateway.sh` that contains:

Copy

    
    
    #!/bin/bash
    set -e  # Exit immediately if a command fails
    
    # Navigate to the directory containing your docker-compose.yml file
    cd /path/to/your/docker-compose-directory
    
    # Pull the latest image and update the Gateway container
    docker compose pull
    docker compose up -d keeper-gateway

Make the script executable:

Copy

    
    
    chmod +x update_gateway.sh

Edit the crontab:

Copy

    
    
    crontab -e

Add a line to schedule the script. For example, to run it every day at 3 AM:

Copy

    
    
    0 3 * * * /path/to/update_gateway.sh >> /var/log/update_gateway.log 2>&1

###

**Linux**

####

**New Gateway**

Execute the following command to download and run the KeeperPAM installer with
auto update enabled.

The `--autoupdate` parameter activates the auto updater in addition to the
Keeper Gateway.

Copy

    
    
    curl -fsSL https://keepersecurity.com/pam/install | \
      sudo bash -s -- --autoupdate

####

**Existing Keeper Gateway**

Activate the Auto Updater on an existing installation by executing the
following Keeper Gateway command:

Copy

    
    
    sudo keeper-gateway autoupdate enable

**Verify Installation (Optional)**

Verify that the Auto Updater has been installed successfully by executing the
following Keeper Gateway command:

Copy

    
    
    sudo keeper-gateway autoupdate status

###

Windows

####

New Gateway

  * Download and run the latest version of the Gateway installer.

  * During installation, check the box "Enable automatic updates".

  * This setup option will create a new Task Scheduler task for updating the Gateway.

**Existing Gateway**

  * Open a command prompt as Administrator.

  * Install Auto Updater with the following Keeper Gateway command:

Copy

    
    
    keeper-gateway autoupdate enable

**Verify Installation (Optional)**

  * Open a command prompt as Administrator.

  * Verify that Auto Updater has been installed successfully by executing the following Keeper Gateway command:

Copy

    
    
    keeper-gateway autoupdate status

##

Auto Updater Status

###

Prerequisites

  * Ensure that you have administrative privileges on the system.

  * Version 1.4.0 or later of Keeper Gateway is required.

###

Status on Linux

Check the Auto Updater status by executing the following Keeper Gateway
command:

Copy

    
    
    sudo keeper-gateway autoupdate status

###

Status on Windows

  * Open a command prompt as Administrator

  * Check the Auto Updater status by executing the following Keeper Gateway command:

Copy

    
    
    keeper-gateway autoupdate status

##

Auto Updater Configuration

###

Configuration on Linux

Edit the crontab that runs Auto Updater.

Copy

    
    
    sudo crontab -e

Here is an example of the default crontab entry that checks for updates every
hour:

Copy

    
    
    0 * * * * /usr/local/bin/keeper-gateway-update --trust

  * The first part `0 * * * *` is the crontab expression which will cause execution to occur every hour at 0 minutes.

  * The second part is the update command `keeper-gateway-update`

  * The option `--trust` causes explicit trust of the Keeper Gateway GPG public key for verification of downloaded install files.

###

Configuration on Windows

Configure the update frequency and other settings with the following steps:

  * Run `taskschd.msc` to open Windows Task Scheduler.

  * In the left pane double-click on Task Scheduler Library -> Keeper -> Gateway -> AutoUpdate to show the Auto Updater Task.

  * In the upper middle pane double-click on the AutoUpdate Task with the name of the current version and click on the Triggers menu tab.

  * Click `Edit...` to change when the Auto Updater checks for a new update to install. The default is to "Repeat task every 1 hour indefinitely" as shown below.

##

Auto Updater Removal

###

Prerequisites

  * Ensure that you have administrative privileges on the system.

  * Version 1.4.0 or later of Keeper Gateway is required.

###

Removal on Linux

Remove Auto Updater by executing the following Keeper Gateway command:

Copy

    
    
    sudo keeper-gateway autoupdate disable

###

Removal on Windows

Remove Auto Updater with the following steps:

  * Open a command prompt as Administrator.

  * Remove Auto Updater with the following Keeper Gateway command:

Copy

    
    
    keeper-gateway autoupdate disable

##

Troubleshooting

###

Check the status of the Auto Update

Copy

    
    
    keeper-gateway autoupdate status

###

Logging in the Gateway Auto Updater

To assist with diagnosing issues or monitoring the status of updates, the
Gateway Auto Updater generates two types of logs. These logs are subject to
rotation policies to avoid overuse of disk space.

###

Linux

**Log Location**

All log files for Linux are located in `/var/log/keeper-gateway`

**Log Files**

  * **Update Logs** : Any logs generated during an update will be timestamped and stored as `update_YYYY-MM-DD_HH-MM-SS.log`.

  * **Last Update Check** : The file `last-update-check.log` contains information regarding the most recent check for updates.

###

Windows

####

**Log Location**

The log files for the Gateway Auto Updater are located in
`\ProgramData\KeeperGateway\install`

**Log Files**

  * **Update Logs** : Any logs generated during an update will be timestamped and stored as `YYYY-MM-DD_HH-MM-SS.log`

  * **Last Update Check** : The file `last-update-check.log` contains information regarding the most recent check for updates.

# Gateway Configuration with Custom Fields

Advanced configuration of the Keeper gateway with Keeper Vault custom fields

These configuration capabilities are functional and currently in an
experimental phase, and we invite users to actively explore and utilize them.
We are actively evaluating their functionality and performance, with the
intention of considering them for official integration into our product in the
future.

##

Advanced Gateway Configuration with Custom Fields

The additional gateway configurations will be defined with these custom fields
on the PAM Record Types. The Keeper Gateway will then adjust its behavior
based on the defined configurations.

The following tables lists all the possible configurations with custom fields:

**Note:**

  * The custom fields values are not case-sensitive.

# Local Environment Setup

Setting up your Local environment to work with KeeperPAM

##

Local Environment Overview

The PAM Configuration contains critical information on your local
infrastructure, settings and associated Keeper Gateway. This guide provides
step-by-step instructions for configuring the PAM Configuration in your local
environment, enabling the Keeper Gateway to manage all resources within it and
allowing users to utilize KeeperPAM features on those resources.

###

Prerequisites

##

Creating PAM Configuration

To create a new PAM Configuration:

  * Login to the Keeper Vault

  * Select Secrets Manager and the "PAM Configurations" tab

  * Click on "New Configuration"

##

PAM Configuration Fields - Local Environment

The following tables provides more details on each configurable fields in the
PAM Configuration record for the local environment:

For Discovery, the following fields are required, otherwise they are optional:

###

PAM Features

The **"PAM Features Allowed"** and **"Session Recording Types Allowed"**
sections in the PAM Configuration allow owners to enable or disable KeeperPAM
features for resources managed through the PAM configuration:

##

Configuring PAM Features on PAM Record Types

After creating the PAM configuration, visit the following pages to:

  *   *   *   *   * 

# PAM Resources

Guide for using PAM Resource Records in the Keeper Vault for privileged access
functionality.

##

Overview

KeeperPAM Resource records are special record types designed to organize and
store information of your target infrastructure, machines, web apps, workloads
and user accounts.

  * 

###

KeeperPAM Record Types

In your Keeper Vault, resources that represent your infrastructure are created
with the following Record Types:

###

Record Linking

###

Creating a PAM Record

From the Vault UI, click on Create New and select either Rotation, Tunnel or
Connection.

Alternatively, you can right-click on a folder and select Rotation, Tunnel or
Connection.

The "Target" selection will determine what type of record will be created.

# AWS Environment Setup

Setting up your AWS environment to work with KeeperPAM

##

AWS Environment Overview

Resources in your AWS environment can be managed by a Keeper Gateway using EC2
instance role policy or using a specified Access Key ID / Secret Access Key
configured in the PAM Configuration record.

The role policy must be configured appropriately to enable access to the
target AWS resources:

  *   * 

The following diagram shows the AWS environment hierarchy:

##

EC2 IAM Role Policy

To create a EC2 IAM policy which supports PAM features such as password
rotation and discovery, a role with the appropriate policy settings should be
configured then attached to the EC2 instance running the Keeper Gateway.

For KeeperPAM to have the authority to rotate IAM users and RDS databases, the
following inline role policy should be modified to meet your needs and ensure
least privilege.

To ensure least privilege, the JSON policy should be modified based on which
target resources that KeeperPAM will be managing through the "Action" and
"Resource" attributes.

Follow these steps to create a new role and apply the policy:

  1. Create role with JSON specified above, or click on IAM > Roles > Create Role > Select "AWS Service" with "EC2 use case".

  2. Attach the policy JSON to the role.

  3. From EC2 > Instances, select the instance with the gateway and go to Actions > Security > Modify IAM Role > Select your new role.

###

Minimum AWS Policy to Manage IAM users

* * *

##

IAM User Policy

Using EC2 instance role policy is preferred, however the AWS Access Key ID and
Secret Access Key can be directly set in the PAM Configuration. The IAM Admin
account needs to be created with the appropriate policy settings configured to
access the target resource in AWS.

An sample policy is below.

To ensure least privilege, the JSON policy should be modified based on which
target resources that KeeperPAM will be managing through the "Action" and
"Resource" attributes.

The steps to create the access keys is below:

  1. Create a new IAM user or select an existing user

  2. Attach the policy to the user

  3. Open the IAM user > Security credentials > Create access key

  4. Select "Application running outside AWS"

  5. Save the provided Access Key ID / Secret Access Key into the PAM Configuration

# PAM Configuration

Creating a PAM Configuration in the Keeper Vault

##

Overview

In Keeper, the **PAM Configuration** contains essential information of your
target infrastructure, settings and associated Keeper Gateway. We recommend
setting up one PAM Configuration for each Gateway and network being managed.

##

Creating PAM Configuration

To create a new PAM Configuration:

  * Login to the Keeper Vault

  * Select Secrets Manager and the "PAM Configurations" tab

  * Click on "New Configuration"

##

PAM Configuration Fields

When setting up the PAM Configuration, you have the option of choosing one of
the following environments:

  *   *   *   * 

The following tables provides more details on each configurable fields in the
PAM Configuration record regardless of the environment you choose:

**Security Note (1)** The PAM Configuration information is stored as a record
in the vault inside the specified **Application Folder** and may contain
secrets. Therefore, we recommend that the Application Folder should be limited
in access to only privileged admins.

The following tables provides more details on each configurable fields in the
PAM Network Configuration record based on the environment you chose:

###

Local Network Environment

###

AWS Environment

  * 

###

Azure Environment

  * 

###

Domain Controller Environment

##

PAM Features on PAM Configuration

The **"PAM Features Allowed"** and **"Session Recording Types Allowed"**
sections in the PAM Configuration allow owners to enable or disable KeeperPAM
features for resources managed through the PAM configuration:

If you are installing on an EC2 instance in AWS, the Keeper Gateway can be
configured to use the instance role for pulling its configuration from AWS
Secrets Manager. Detailed instructions on this setup can be .

See the  of a Device

See more details on the

This document contains information on how to install, configure, and update
your Keeper Gateway on Docker. The Docker container is built upon the base
image of Rocky Linux 8 and it is hosted in .

`docker` and `docker-compose` installed (see  for help)

DockerHub listing:

Quick reference for

To initialize a Gateway for  or  native install methods, the one-time token
method is used:

To initialize a Gateway using Docker, the base64 configuration is provided as
`GATEWAY_CONFIG` environment variable as described in the  instructions.

Prior to proceeding with this document, make sure you .

If you cannot use one of these Linux flavors, please install using the

The Keeper Gateway configuration file contains a set of tokens that includes
encryption keys, client identifiers, and tenant server information used to
authenticate and decrypt data from the Keeper Secrets Manager APIs. This
configuration file is created from the One-Time Access Token generated when
you .

Prior to proceeding with this document, make sure you .

Upon installation of the service, select "Enter a Keeper One-Time Access
Token" and supply the token provided by when you  on the Vault. After
installation, the service will automatically start up and register with the
Keeper cloud.

Use service account - Use the , otherwise the account installing the gateway
will be used.

Turn on debug logging - Enable  on the gateway log files. NOT recommended for
production environments. Only use this when debugging with Keeper support.

The final step prior to successfully installing the Keeper Gateway as service
is to enter the  Token provided from the Keeper Vault.

The Keeper Gateway configuration file contains a set of tokens that includes
encryption keys, client identifiers, and tenant server information used to
authenticate and decrypt data from the Keeper Secrets Manager APIs. This
configuration file is created from the One-Time Access Token generated when
you .

See

Run custom reports from the Keeper Admin Console or  CLI

When setting up Rotation in your Keeper Vault, you store the credentials of
your assets involved in rotation on their corresponding PAM Record Types. On
these record types, you are able to .

Custom Field Name

Type

Default Value

Description

Prior to proceeding with this guide, make sure to .

Field

Description

Notes

Field

Description

Notes

Field

Description

Configure

Configure

Configure

Configure

Configure

PAM Record Type

Target Infrastructure

The PAM User record is special because it can be  from the other resources.
This way, you can  to a Machine, Database, Directory or Remote Browser without
sharing access to the underlying credentials.

Managed User Type

IAM Policy

In addition to these policies, we recommend protecting the Gateway
Configuration secrets .

Field

Description

Notes

Field

Description

Notes

Field

Description

Notes

See additional information on

Field

Description

Notes

See additional information on

Field

Description

Required

Field

Description

**Docker**

**Windows**

**Linux**

Docker

Linux

Windows

found here

[Security & Encryption
Model](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/security-encryption-model)

[One-Time Access Token
details](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/one-time-token)

[Secrets Manager Configuration
details](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/about/secrets-manager-configuration)

[secrets-manager Commander CLI
command](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-cli/command-
reference/secrets-manager-commands)

[DockerHub](https://hub.docker.com/r/keeper/gateway)

[Docker Install](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/references/installing-docker-on-linux)

<https://hub.docker.com/r/keeper/gateway>[](https://hub.docker.com/r/keeper/gateway)

[Installing Docker](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/references/installing-docker-on-linux)

[ and Docker Compose on
Linux](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/references/installing-docker-on-linux)

[Quick Start:
Sandbox](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/quick-start-sandbox)

Linux

Windows

Docker Installation

created a Gateway device

Docker method

created the Gateway

Activate the Auto Updater

created a Gateway device

[**Download the Keeper Gateway for
Windows**](https://keepersecurity.com/pam/gateway/keeper-
gateway_windows_x86_64.exe)

created a Gateway

One-Time Access

created the Gateway

Storing Gateway Configuration in AWS KMS

Gateway Configuration with Custom Fields

Docker Installation

Linux Installation

`Shell`

Text

`None`

Allows you to specify a custom shell path that the Gateway will use when
executing rotation and post-rotation scripts. This gives you control over the
environment in which these scripts run. Example Value: `C:\MY\SHELL`

`NOOP`

Text

`False`

Allows you to control whether the Gateway performs the primary rotation
operation or proceeds directly to execution of the post-rotation script.

If set to `True` the Gateway will skip the rotation process and proceed
directly in executing the post-rotation script(s). Example Value: `True`

`Kerberos`

Text

`False`

Specifically designed for WinRM connections using Kerberos authentication. By
default, the Gateway automatically decides whether to use Kerberos based on
certain rules, and If these conditions are met, the Gateway will attempt to
use Kerberos for WinRM. However, if you encounter issues with this automatic
detection, setting this field to `True` will override the default behavior and
force the Gateway to use Kerberos for WinRM. Example Value: `True`

`Private Key Type`

Text

`ssh-rsa`

Gateway Version 1.3.4+ This custom field pertains to the type or algorithm of
the private key stored in a record. When adding a private key to a record,
users do not need to take any additional action regarding its type or
algorithm. The system is designed to automatically recognize and use the same
algorithm as the existing private key during the rotation process. If the
algorithm in use is ECDSA, the key size will also be preserved during the
rotation. Available Options if needed to overwrite the key type: `ssh-rsa`
(Note: 4096 bits)

`ssh-dss` (Note: 1024 bit, obsolete) `ecdsa-sha2-nistp256`

`ecdsa-sha2-nistp384`

`ecdsa-sha2-nistp521`

`ssh-ed25519`

`Private Key Rotate`

Text

`True`

Gateway Version 1.3.4+

`TRUE` \- (Default) If the custom field doesn't exist, the private key will be
rotated if it exists.

`FALSE` \- The private key won't be rotated, even if it exists. Users should
pick this if they wish to retain the private key in the record without any
rotations.

Rotation

If enabled, allow rotations on privileged user users managed by this PAM
configuration

Connections

If enabled, allow connections on resources managed by this PAM configuration

Remote Browser Isolation (RBI)

If enabled, allow RBI sessions on resources managed by this PAM configuration

Tunneling

If enabled, allow tunnels on resources managed by this PAM configuration

Graphical Session Recording

If enabled, visual playback sessions will be recorded for all connections and
RBI sessions

Text Session Recording (TypeScript)

If enabled, text input and output logs will be logged for all connections and
RBI sessions

Copy

    
    
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "iam:SimulatePrincipalPolicy",
                    "ec2:DescribeInstances",
                    "rds:DescribeDBInstances",
                    "ds:DescribeDirectories",
                    "iam:ListUsers",
                    "iam:GetUser",
                    "iam:ListAccessKeys",
                    "iam:UpdateLoginProfile",
                    "rds:ModifyDBInstance",
                    "ds:ResetUserPassword",
                    "ds:DescribeLDAPSSettings",
                    "ds:DescribeDomainControllers"
                ],
                "Resource": "*"
            }
        ]
    }

EC2 User

Rotation uses local credentials and no specific AWS permissions are needed.

Managed Database

Rotation uses AWS APIs for PAM Database records and requires: **iam:GetUser
iam:SimulatePrincipalPolicy rds:ModifyDBInstance rds:DescribeDBInstances**

For managing PAM Database or PAM User Records via SQL no AWS permissions are
needed.

Directory User

Rotation uses AWS APIs for PAM Directory records and requires:

**iam:SimulatePrincipalPolicy ds:DescribeDirectories ds:ResetUserPassword
ds:DescribeLDAPSSettings ds:DescribeDomainControllers**

IAM User

Rotation uses AWS APIs for PAM User records and requires:

**iam:SimulatePrincipalPolicy iam:UpdateLoginProfile iam:GetUser**

Copy

    
    
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "iam:SimulatePrincipalPolicy",
                    "ec2:DescribeInstances",
                    "rds:DescribeDBInstances",
                    "ds:DescribeDirectories",
                    "iam:ListUsers",
                    "iam:GetUser",
                    "iam:ListAccessKeys",
                    "iam:UpdateLoginProfile",
                    "rds:ModifyDBInstance",
                    "ds:ResetUserPassword",
                    "ds:DescribeLDAPSSettings",
                    "ds:DescribeDomainControllers"
                ],
                "Resource": "*"
            }
        ]
    }

AWS ID

A unique id for the instance of AWS

Required, This is for the user's reference Ex: `AWS-US-EAST-1`

Access Key ID

From an IAM user account, the Access key ID from the desired Access key.

Leave Empty when EC2 instance role is assumed.

Secret Access Key

The secret key for the access key.

Leave Empty when EC2 instance role is assumed.

Region Names

AWS region names used for discovery. Separate newline per region

Ex: us-east-2 us-west-1

Port Mapping

Any non-standard ports referenced. Separate newline per entry

Ex: 2222=ssh 3390=rdp

Azure ID

A unique id for your instance of Azure

Required, This is for the user's reference Ex: `Azure-1`

Client ID

The application/client id (UUID) of the Azure application

Required

Client Secret

The client credentials secret for the Azure application

Required

Subscription ID

The UUID of the subscription (i.e. Pay-As-You-GO).

Required

Tenant ID

The UUID of the Azure Active Directory

Required

Resource Groups

A list of resource groups to be checked. If left blank, all resource groups
will be checked. Newlines should separate each resource group.

DNS Domain Name

The FQDN domain used by the Domain Controller. For example, EXAMPLE.COM and
not EXAMPLE.

Yes

Hostname and Port

Hostname and port for the domain controller.

Yes

Use SSL

If using LDAPS (default 636), check the box. If using LDAP (default 389),
uncheck the box.

Yes

Scan Network

Scan the CIDRs from the domain controller. Default to False.

No

Network CIDR

Scan additional CIDRs from the field.

No

Port Mapping

Define alternative default ports

No

Rotation

If enabled, allow rotations on privileged user users managed by this PAM
configuration

Connections

If enabled, allow connections on resources managed by this PAM configuration

Remote Browser Isolation (RBI)

If enabled, allow RBI sessions on resources managed by this PAM configuration

Tunneling

If enabled, allow tunnels on resources managed by this PAM configuration

Graphical Session Recording

If enabled, visual playback sessions will be recorded for all connections and
RBI sessions

Text Session Recording (TypeScript)

If enabled, text input and output logs will be logged for all connections and
RBI sessions

[create custom fields](https://docs.keeper.io/enterprise-guide/record-
types#custom-fields)

install and configure your Keeper Gateway

[Rotation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/password-rotation)

[Connections](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/connections)

[RBI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[Tunnels](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/tunnels)

[Discovery](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/discovery)

[What's a Record Type?](https://docs.keeper.io/en/enterprise-guide/record-
types)

linked

share access

using the AWS KMS

AWS Environment Setup

Azure Environment Setup

specified service account

verbose logging

Title (Required)

Name of PAM configuration record

Ex: Local Configuration

Environment (Required)

Your infrastructure's environment

For this guide, select "Local"

Gateway (Required)

The configured gateway

Application Folder (Required)

The shared folder where the PAM Configuration data will be stored

Best practice is to create a folder with limited access to admins. See
Security Note (1) below

PAM Settings (Required)

List of Zero-Trust KeeperPAM features that should be enabled

Default Rotation Schedule

Specify frequency of Rotation

Ex: `Daily`

Port Mapping

Define alternative default ports

Network ID

Unique ID for the network

This is for the user's reference

Ex: `My Network`

Network CIDR

Subnet of the IP address

Windows/macOS/Linux Machines, EC2 Instances, Azure VMs, etc.

MySQL, PostgreSQL, SQL Server, MongoDB, MariaDB, Oracle

Active Directory, OpenLDAP

Web-based Applications, internal apps or cloud apps

Any local user, remote user, database credential or admin account. PAM User
records can also be configured for scheduled or on-demand password rotation.

Title

Name of PAM configuration record

Ex: `US-EAST-1 Config`

Gateway

The configured gateway

Application Folder

The shared folder where the PAM Configuration data will be stored

Best practice is to create a folder with limited access to admins. See
Security Note (1) below

PAM Settings

List of Zero-Trust KeeperPAM features that should be enabled

Default Rotation Schedule

Specify frequency of Rotation

Ex: `Daily`

Port Mapping

Define alternative default ports

Network ID

Unique ID for the network

This is for the user's reference

Ex: `My Network`

Network CIDR

Subnet of the IP address

# Example: Azure Windows VM

Configuring an Azure Windows VM as a PAM Machine Record

##

Overview

In this example, you'll learn how to configure a Azure Windows VM in your
Keeper Vault as a PAM Machine record.

##

Prerequisites

Prior to proceeding with this guide, make sure you have

  1.   2. 

##

PAM Machine Record

Machines such as a Azure Virtual Machines can be configured on the PAM Machine
record type.

###

Creating a PAM Machine

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Machine** " for the Target 

  * Click "**Next** " and complete all of the required information.

###

Configure a Windows Machine on the PAM Machine Record

Suppose I have a Azure Virtual Machine with the hostname "10.0.1.4", the
following table lists all the configurable fields and their respective values:

Field

Description

Value

Title (Required)

Title of the PAM Machine Record

`Windows VM`

Hostname or IP Address (Required)

Address or RDP endpoint or Server name of the Machine Resource

`10.0.1.4`

Port (Required)

Port to connect to the Azure VM for rotation. 22 for SSH, 5986 for WinRM

5986

Operating System

The target's Operating System

Set to: `Windows`

Instance Name

Azure or AWS Instance Name

**Required** if AWS/Azure Machine `webserver-prod-01`

Instance ID

Azure or AWS Instance ID

**Required** if AWS/Azure Machine

Provider Group

Azure or AWS Provider Group

**Required** if a managed Azure Machine

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS Machine

###

Configuring PAM Settings on the PAM Machine

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential. The following table lists all the configurable fields and their
respective values for the Azure Virtual Machine:

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required -** This is the PAM configuration you created in the prerequisites

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native protocol used for connecting from the Gateway to the target

**Required -** for this example: "RDP"

Session Recording

Options for recording sessions and typescripts

Connection Parameters

Connection-specific protocol settings which can vary based on the protocol
type

###

Administrative Credential Record

The **Admin Credential Record** in the PAM Machine links the admin user to the
PAM Machine record in your Keeper Vault. This admin user is used for
performing password rotations and authenticating connections.

####

Setting a Non Admin User as the Administrative Credential Record

If you prefer not to authenticate a connection using the admin credential, you
can optionally designate a regular user of the resource as the admin
credential.

##

Sharing PAM Machine Records

PAM Machine records can be shared with other Keeper users within your
organization. However, the recipient must have the appropriate PAM enforcement
policies in place to utilize KeeperPAM features on the shared PAM records.

When sharing a PAM Machine record, the linked admin credentials will **not**
be shared. For example, if the PAM Machine is configured with a Azure Virtual
Machine, the recipient can connect to the Azure Virtual Machine on the PAM
Machine record without having direct access to the linked credentials.

  * 

# Example: Linux Machine

Configuring SSH Server as a PAM Machine Record

##

Overview

In this example, you'll learn how to configure a Linux Machine in your Keeper
Vault as a PAM Machine record.

##

Prerequisites

Prior to proceeding with this guide, make sure you have

  1.   2. 

##

PAM Machine Record

Machines such as a Linux Machines can be configured on the PAM Machine record
type.

###

Creating a PAM Machine

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Machine** " for the Target 

  * Click "**Next** " and complete all of the required information.

###

Configure a Linux Machine on the PAM Machine Record

Suppose I have a local Linux Virtual Machine with the hostname "linux-
machine", the following table lists all the configurable fields and their
respective values:

Field

Description

Value

Title (Required)

Title of the PAM Machine Record

`Linux Machine`

Hostname or IP Address (Required)

Address or RDP endpoint or Server name of the Machine Resource

linux-machine

Port (Required)

Port to connect to the Linux Resource

22

Operating System

The target's Operating System

`linux`

Instance Name

Azure or AWS Instance Name

**Required** if AWS/Azure Machine

Instance ID

Azure or AWS Instance ID

**Required** if AWS/Azure Machine

Provider Group

Azure or AWS Provider Group

**Required** if a managed Azure Machine

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS Machine

###

Configuring PAM Settings on the PAM Machine

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential. The following table lists all the configurable fields and their
respective values for the Linux Machine:

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required -** This is the PAM configuration you created in the prerequisites

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native protocol used for creating a session from the Gateway to the target

**Required -** for this example: "SSH"

Session Recording

Options for recording sessions and typescripts

Connection Parameters

Connection-specific protocol settings which can vary based on the protocol
type.

###

Administrative Credential Record

The **Admin Credential Record** in the PAM Machine links the admin user to the
PAM Machine record in your Keeper Vault. This admin user is used for
performing password rotations and authenticating connections.

####

Setting a Non Admin User as the Administrative Credential Record

If you prefer not to authenticate a connection using the admin credential, you
can optionally designate a regular user of the resource as the admin
credential.

##

Sharing PAM Machine Records

When sharing a PAM Machine record, the linked admin credentials will **not**
be shared. For example, if the PAM Machine is configured with a Linux Machine,
the recipient can connect to the Linux Machine on the PAM Machine record
without having direct access to the linked credentials.

  * 

# PAM Machine

KeeperPAM resource for managing machines on-prem or in the cloud

##

Overview

A PAM Machine record is a type of KeeperPAM resource that represents a
workload, such as a Windows or Linux server.

PAM Record Type

Supported Assets

PAM Machine

Windows/macOS/Linux Machines, EC2 Instances, Azure VMs

##

Features Available

The PAM Machine resource supports the following features:

  * Password rotation

  * SSH key rotation

  * Zero-trust Connections using RDP, SSH, VNC, K8s and Telnet protocols

  * TCP Tunnels

  * Session recording

  * Sharing access without sharing credentials

  * File transfer through drag-and-drop

##

Creating a PAM Machine

Prior to creating a PAM Machine, make sure you have already created a PAM
Configuration. The PAM Configuration contains information of your target
infrastructure while the PAM Machine contains information of an asset, such as
a Windows or Linux server.

To create a PAM Machine:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Machine** " for the Target 

  * Click "**Next** " and complete all of the required information.

##

PAM Machine Record Type Fields

The following table lists all the configurable fields on the PAM Machine
Record Type:

Field

Description

Notes

Hostname or IP Address

Address of the machine resource

**Required**

Port

Port to connect on. The Gateway uses this to determine connection method.

**Required** Must be a port for SSH or WinRM

Keeper expects 22, 5985, 5986, or an alternative port for SSH or WinRM
specified in the PAM Configuration port mapping

Administrative Credentials

Linked PAM User credential used for connection and administrative operations

PAM settings

This is where you configure Connection and Tunnel settings for this machine.

Operating System

The target's Operating System

For your reference only

SSL Verification

When checked, verifies certificate of host when connecting with SSH

Only applies to certain databases and directories where SSL is optional

Instance Name

Azure or AWS Instance Name

**Required** if AWS/Azure Machine

Instance Id

Azure or AWS Instance ID

**Required** if AWS/Azure Machine

Provider Group

Provider Group for directories hosted in Azure

**Required** if Azure Machine

Provider Region

AWS region of hosted directory

**Required** if AWS Machine

##

PAM Settings and Administrative Credentials

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential.

###

PAM Settings

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required**

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

**Required**

Protocol

Native protocol used for connecting the session from the Gateway to the target

**Required**

Session Recording

Options for recording sessions and typescripts

Connection Parameters (multiple)

Connection-specific protocol settings which can vary based on the protocol
type

Depends on protocol. We recommend specifying the **Connection Port** at a
minimum.

Below are a couple examples of PAM Machine records with Connections and
Tunnels activated.

##

Examples

Visit the following pages to set up:

  *   * 

# Example: MySQL Database

Configuring MySQL DB as a PAM Database Record

##

Overview

In this example, you'll learn how to configure a MySQL DB in your Keeper Vault
as a PAM Database record.

##

Prerequisites

Prior to proceeding with this guide, make sure you have

  1.   2. 

##

PAM Database Record

Databases such as a MySQL DB can be configured on the PAM Database record
type.

###

Creating a PAM Database

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Database** " for the Target 

  * Click "**Next** " and complete all of the required information.

###

Configure a MySQL Database on the PAM Database Record

Suppose I have a database with the hostname "db-mysql-1", the following table
lists all the configurable fields and their respective values:

Field

Description

Value

Title (Required)

Title of the PAM Database Record

`Local MySQL Database`

Hostname or IP Address (Required)

Address or RDP endpoint or Server name of the Database Resource

db-mysql-1

Port (Required)

Port to connect to the Database Resource

3306

Use SSL (Required)

Check to perform SSL verification before connecting, if your database has SSL
configured

`Enabled`

Database ID

Azure or AWS Resource ID (if applicable)

**Required** if a managed AWS or Azure Database

Database Type

Appropriate database type from supported databases.

`mysql`

Provider Group

Azure or AWS Provider Group

**Required** if a managed AWS or Azure Database

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS or Azure Database

###

Configuring PAM Settings on the PAM Database

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential. The following table lists all the configurable fields and their
respective values for the MySQL Database:

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required -** This is the PAM configuration you created in the prerequisites

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native database protocol used for connecting from the Gateway to the target

**Required -** for this example: "MySQL"

Session Recording

Options for recording sessions and typescripts

Connection Parameters

Connection-specific protocol settings which can vary based on the protocol
type

###

Administrative Credential Record

The **Admin Credential Record** in the PAM Database links a user to the PAM
Database record in your Keeper Vault. This linked user is used for
authenticating the connection when clicking "Launch".

####

Setting a Non Admin User as the Administrative Credential Record

If you prefer not to authenticate a connection using the admin credential, you
can optionally designate a regular user of the resource as the admin
credential.

##

Sharing PAM Database Records

PAM Database records can be shared with other Keeper users within your
organization. However, the recipient must be assigned to a role with the
appropriate PAM enforcement policies in place to utilize KeeperPAM features.

When sharing a PAM Database record, the linked admin credentials will **not**
be shared. For example, if the PAM Database is configured with a MySQL
Database, the recipient can connect to the database without having direct
access to the linked credentials.

  * 

###

Setup Complete

The MySQL Database record is set up. The user with the ability to launch
connections can now launch an interactive MySQL connection or tunnel to the
target database.

# Example: PostgreSQL Database

Configuring PostgreSQL DB as a PAM Database Record

##

Overview

In this example, you'll learn how to configure a PostgreSQL DB in your Keeper
Vault as a PAM Database record.

##

Prerequisites

Prior to proceeding with this guide, make sure you have

  1.   2. 

##

PAM Database Record

Databases such as a PostgreSQL DB can be configured on the PAM Database record
type.

###

Creating a PAM Database

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Database** " for the Target 

  * Click "**Next** " and complete all of the required information.

###

Configure a PostgreSQL Database on the PAM Database Record

Suppose I have a database with the hostname "`db-postgres-1`", the following
table lists all the configurable fields and their respective values:

Field

Description

Value

Title (Required)

Title of the PAM Database Record

`PostgreSQL Database - postgresuser`

Hostname or IP Address (Required)

Address or RDP endpoint or Server name of the Database Resource

db-postgres-1

Port (Required)

Port to connect to the PostgreSQL DB Resource

5432

Use SSL (Required)

Check to perform SSL verification before connecting, if your database has SSL
configured

`Enabled`

Database ID

Azure or AWS Resource ID (if applicable)

**Required** if a managed AWS or Azure Database

Database Type

Appropriate database type from supported databases.

`postgresql`

Provider Group

Azure or AWS Provider Group

**Required** if a managed AWS or Azure Database

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS or Azure Database

###

Configuring PAM Settings on the PAM Database

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential. The following table lists all the configurable fields and their
respective values for the PostgreSQL Database:

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required -** This is the PAM configuration you created in the prerequisites

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native database protocol used for connecting from the Gateway to the target

**Required -** for this example: "PostgreSQL"

Session Recording

Options for recording sessions and typescripts

Connection Parameters

Connection-specific protocol settings which can vary based on the protocol
type

###

Administrative Credential Record

The **Admin Credential Record** in the PAM Database links a user to the PAM
Database record in your Keeper Vault. This linked user is used for
authenticating the connection when clicking "Launch".

####

Setting a Non Admin User as the Administrative Credential Record

If you prefer not to authenticate a connection using the admin credential, you
can optionally designate a regular user of the resource as the admin
credential.

##

Sharing PAM Database Records

PAM Database records can be shared with other Keeper users within your
organization. However, the recipient must be assigned to a role with the
appropriate PAM enforcement policies in place to utilize KeeperPAM features.

When sharing a PAM Database record, the linked admin credentials will **not**
be shared. For example, if the PAM Database is configured with a PostgreSQL
Database, the recipient can connect to the database without having direct
access to the linked credentials.

  * 

###

Setup Complete

The PostgreSQL Database record is set up. The user with the ability to launch
connections can now launch an interactive PostgreSQL connection or tunnel to
the target database.

# PAM Database

KeeperPAM resource for managing databases either on-prem or in the cloud

##

Overview

In your Keeper Vault, the following assets can be configured on the PAM
Database record type:

PAM Record Type

Supported Assets

PAM Database

MySQL, PostgreSQL, SQL Server, MongoDB, MariaDB, Oracle

This guide will cover the **PAM Database** Record type in more details.

##

Features Available

The PAM Database resource supports the following features:

  * Password rotation

  * Zero-trust Connections

  * TCP Tunnels

  * Graphical session recording

  * Text session recording (Typescript)

  * Sharing access without sharing credentials

##

Creating a PAM Database

Prior to creating a PAM Database, make sure you have already created a PAM
Configuration. The PAM Configuration contains information of your target
infrastructure while the PAM Database contains information about the target
database, such as the hostname, type (MySQL, PostgreSQL, etc) and port number.

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Database** " for the Target 

  * Click "**Next** " and complete all of the required information.

##

PAM Database Record Type Fields

The following table lists all the configurable fields on the PAM Database
Record Type:

Field

Description

Notes

Hostname or IP Address

Address of the Database Resource

**Required**

Port

Port to connect to the Database Resource

**Required** Standard ports are: PostgreSQL: 5432 MySQL: 3306 Maria DB: 3306
Microsoft SQL: 1433 Oracle: 1521 Mongo DB: 27017

Use SSL

Use SSL when connecting

Connect Database

Database name to connect to

**Required** for connecting to PostgreSQL, MongoDB, and MS SQL Server

Database Id

Azure or AWS Resource ID

**Required** if a managed AWS or Azure Database

Database Type

Appropriate database type from supported databases.

If a non-standard port is provided, the Database Type will be used to
determine connection method.

Provider Group

Azure or AWS Provider Group

**Required** if a managed AWS or Azure Database

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS or Azure Database

##

PAM Settings and Administrative Credentials

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential.

###

PAM Settings

Field

Description

Required

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required**

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native database protocol used for connecting from the Gateway to the target

**Required**

Session Recording

Options for recording sessions and typescripts

Connection Parameters (multiple)

Connection-specific protocol settings which can vary based on the protocol
type

Depends on protocol

Below is an example of a PAM Database record with Connections and Tunnels
activated.

##

Examples

Visit the following pages to set up:

  *   *   * 

# PAM User

Record Type Details for PAM User Record Type

##

Overview

A PAM User is a type of KeeperPAM resource that represents an account
credential. The PAM User is typically linked from other resources.

##

What is a PAM User

KeeperPAM User records define a specific account inside another PAM resource.
PAM Machines, PAM Databases, PAM Directories and PAM Remote Browser records
link to a PAM User.

##

Features Available

The PAM User resource supports the following features:

  * On-demand and scheduled password rotation

  * PAM Scripts for privilege automation

  * Sharing with time-limited access

##

Creating a PAM User

Prior to creating a PAM User, make sure you have already created a PAM
Configuration and a PAM Resource such as a Machine, Database, Directory or
Browser.

To create a PAM User:

  * Click on **Create New**

  * Depending on your use case, click on "**Rotation** ", "**Tunnel** ", or "**Connection** " 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**User** " for the Target 

  * Click "**Next** " and complete all of the required information.

##

PAM **User** Record Type Fields

The following table lists all the configurable fields on the PAM Remote
Browser Record Type:

####

Note(1)

When connecting to Windows machines that are domain-joined:

  * For domain-joined systems, always use the UPN format (`user@domain.local`) as it is more modern, DNS-reliant, and avoids NetBIOS issues.

  * Reserve `DOMAIN\user` for older systems or mixed environments where UPN isn't supported.

###

Configure rotation settings

# PAM Remote Browser

KeeperPAM resource for managing remote browser isolation access to a protected
web application

##

Overview

A PAM Remote Browser is a type of KeeperPAM resource that represents a remote
browser isolation target, such as a protected internal application or cloud-
based web app.

##

What is Remote Browser Isolation

KeeperPAM remote browser isolation records provide secure access to internal
and cloud-based web applications through a protected browser, embedded within
the vault. This browser is projected visually from the Keeper Gateway through
the Keeper Vault, isolating the session and providing zero-trust access.

##

Features Available

The PAM Remote Browser resource supports the following features:

  * Zero-trust Connections over http:// and https:// websites

  * Session recording

  * Sharing access without sharing credentials

  * Autofill of linked credentials and 2FA codes

  * URL AllowList patterns

  * Navigation bar

##

Creating a Remote Browser Isolation Record

Prior to creating a PAM Remote Browser, make sure you have already created a
PAM Configuration. The PAM Configuration contains information of your target
infrastructure while the PAM Remote Browser contains information about the
target web application and associated access rules.

To create a PAM Remote Browser:

  * Click on **Create New**

  * Select "**Connection** " 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Browser** " for the Target 

  * Click "**Next** " and complete all of the required information.

##

PAM **Remote Browser** Record Type Fields

The following table lists all the configurable fields on the PAM Remote
Browser Record Type:

##

PAM Settings and Administrative Credentials

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and link a PAM User credential for performing autofill.

###

PAM Settings

# Just-In-Time Access (JIT)

KeeperPAM Just-In-Time Access and Zero Standing Privilege

##

Just-In-Time Access and Zero Standing Privilege

###

Introduction

KeeperPAM provides comprehensive just-in-time (JIT) access capabilities to
help organizations achieve zero standing privilege (ZSP) across their entire
IT infrastructure and endpoints. By implementing JIT access controls,
organizations can significantly reduce their attack surface by ensuring that
privileged access is only granted when needed, for the duration required, and
with appropriate approvals.

###

Understanding JIT and ZSP

**Just-In-Time (JIT) Access** : Provides users with privileged access only at
the moment they need it, for a limited time period, and often with approval
workflows.

**Zero Standing Privilege (ZSP)** : A security approach where users have no
permanent privileged access to systems, eliminating the risk associated with
compromised privileged accounts.

###

Use Cases

KeeperPAM offers JIT capabilities across multiple scenarios:

###

Just-in-Time Elevated Access to Infrastructure

Keeper's zero-trust privileged sessions can be established to any target with
a single click from the web vault. When configured for JIT, elevated
privileges are only granted for the duration of the session and automatically
revoked upon session termination.

**Supported Connection Protocols:**

  * RDP (Remote Desktop Protocol)

  * SSH (Secure Shell)

  * VNC (Virtual Network Computing)

  * HTTP/HTTPS

  * Database connections (MySQL, PostgreSQL, SQL Server, Oracle, etc.)

**How to Configure:**

  1. In the KeeperPAM resource configuration, navigate to the "JIT" tab

  2. Enable just-in-time elevated access for the target resource

  3. Configure the elevation settings (Ephemeral account or Group/Role elevation)

  4. Update the configuration

####

Ephemeral Account Creation

KeeperPAM can create temporary accounts with appropriate privileges that exist
only for the duration of a privileged session.

**Key Features:**

  * Automatic creation of temporary privileged accounts when sessions begin

  * Dynamic privilege assignment based on access requirements

  * Complete account removal when sessions terminate

  * No persistent privileged accounts to be compromised

  * Comprehensive logging of all account creation and removal activities

**Benefits:**

  * Eliminates attack vectors associated with standing privileged accounts

  * Prevents lateral movement using compromised credentials

  * Creates clean audit trails linking specific sessions to temporary accounts

  * Reduces administrative overhead of managing privileged accounts

The Keeper Gateway is responsible for creating a temporary account on the
target using the selected account type.

Keeper can create ephemeral accounts on any assigned target resource, such as:

  * Active Directory / LDAP User

  * Windows User

  * Linux User

  * MySQL User

  * PostgreSQL User

  * Microsoft Server SQL User

####

Group and Role Elevation

Role elevation can be assigned at the Group or Role level. For example, an AWS
group or role can be assigned to the connecting user account for the duration
of the session.

In the input field, provide Keeper with the identifier of the group or role to
elevate during the connection. E.g. for Windows this might be “Administrators”
and for AWS this would be the full ARN (e.g. `arn:aws:iam::12345:role/Admin`).

* * *

###

Just-in-Time Elevated Access on Endpoints using PEDM

**Key Features:**

  * Process-level privilege management across Windows, macOS, and Linux

  * Policy-based elevation rules with granular controls

  * User-initiated elevation requests with approval workflows

  * Comprehensive auditing and reporting

**How it Works:**

  1. Users operate with standard, non-privileged accounts by default

  2. When administrative privileges are needed, users request elevation for specific tasks

  3. Based on policy, requests are auto-approved or routed for manual approval

  4. Elevated privileges are granted only for the specified process or time window

  5. Full audit trails capture all elevation activities

For more information see:

  * 

* * *

###

Time-Limited Access with Automated Credential Rotation

KeeperPAM provides time-bounded access to resources with automatic credential
rotation.

**Key Features:**

  * Automated credential rotation on-demand or on a scheduled basis

  * Time-limited access window for authorized users

  * Integration with password rotation policies

  * Complete audit trail of credential changes

**Security Benefits:**

  * Ensures credentials are never re-used for future sessions

  * Protects against credential theft during access periods

  * Creates cryptographically verifiable access boundaries

  * Maintains compliance with credential rotation requirements

To provide time-limited access to a resource, open the resource from the vault
and select **Sharing**. Add the user as a share recipient, and select **Set
Expiration**.

For more information see:

  *   * 

###

Workflow and Requests for Approval

KeeperPAM includes flexible approval workflows for JIT access requests,
ensuring proper oversight of privileged access.

**Key Features:**

  * Multi-level approval workflows

  * Time-based auto-approval or denial

  * Delegation of approval authority

  * Email and mobile notifications

  * Detailed justification requirements

  * Single-user mode (Check-in / Check-out)

  * MFA enforcement on access

**Configuration Options:**

  * Required approvers based on resource sensitivity

  * Approval timeouts and escalations

  * Working hours restrictions

  * Maximum session duration settings

  * User-specific approval requirements

###

Implementation Best Practices

When implementing JIT access and ZSP with KeeperPAM:

  1. **Start with critical systems** : Begin your implementation with your most sensitive systems and infrastructure

  2. **Define clear policies** : Establish clear guidelines for when JIT access is required and who can approve it

  3. **Educate users** : Ensure users understand how to request elevated access when needed

  4. **Monitor and adjust** : Regularly review logs and adjust policies based on actual usage patterns

  5. **Plan for emergencies** : Establish break-glass procedures for critical situations where normal approval workflows may be too slow

###

Conclusion

KeeperPAM's comprehensive JIT and ZSP capabilities provide organizations with
the tools needed to significantly reduce their privileged access attack
surface. By implementing these capabilities across your infrastructure, you
can ensure that privileged access is strictly controlled, properly approved,
and thoroughly audited.

# Example: Microsoft SQL Server Database

Configuring Microsoft SQL Server DB as a PAM Database Record

##

Overview

In this example, you'll learn how to configure a Microsoft SQL Server DB in
your Keeper Vault as a PAM Database record.

##

Prerequisites

Prior to proceeding with this guide, make sure you have

  1.   2. 

##

PAM Database Record

Databases such as a Microsoft SQL Server DB can be configured on the PAM
Database record type.

###

Creating a PAM Database

To create a PAM Database:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Database** " for the Target 

  * Click "**Next** " and complete all of the required information.

###

Configure a Microsoft SQL Server Database on the PAM Database Record

Suppose I have a database with the hostname "`db-mssql-1`", the following
table lists all the configurable fields and their respective values:

###

Configuring PAM Settings on the PAM Database

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential. The following table lists all the configurable fields and their
respective values for the Microsoft SQL Database:

###

Administrative Credential Record

The **Admin Credential Record** in the PAM Database links a user to the PAM
Database record in your Keeper Vault. This linked user is used for
authenticating the connection when clicking "Launch".

####

Setting a Non Admin User as the Administrative Credential Record

If you prefer not to authenticate a connection using the admin credential, you
can optionally designate a regular user of the resource as the admin
credential.

##

Sharing PAM Database Records

PAM Database records can be shared with other Keeper users within your
organization. However, the recipient must be assigned to a role with the
appropriate PAM enforcement policies in place to utilize KeeperPAM features.

When sharing a PAM Database record, the linked admin credentials will **not**
be shared. For example, if the PAM Database is configured with a Microsoft SQL
Database, the recipient can connect to the database without having direct
access to the linked credentials.

  * 

###

Setup Complete

The Microsoft SQL Database record is set up. The user with the ability to
launch connections can now launch an interactive SQL connection or tunnel to
the target database.

# PAM Directory

KeeperPAM resource for managing directory services, either on-prem or in the
cloud

##

Overview

A PAM Directory record is a type of KeeperPAM resource that represents an
Active Directory or OpenLDAP service, either on-prem or hosted in the cloud.

##

Features Available

The PAM Machine resource supports the following features:

  * Password rotation using either LDAP, LDAPS or WinRM

  * Connections using RDP

  * TCP Tunnels over any protocol

  * Session recording and playback

  * Sharing access without sharing credentials

##

Creating a PAM Directory

Prior to creating a PAM Directory Record type, make sure you have already
created a PAM Configuration. The PAM Configuration contains information of
your target infrastructure while the PAM Directory contains information of an
asset, such as a Active Directory server, within that target infrastructure.

To create a PAM Directory:

  * Click on **Create New**

  * Depending on your use case, click on "Rotation", "Tunnel", or "Connection" 

  * On the prompted window:

    * Select "**New Record** " 

    * Select the Shared Folder you want the record to be created in 

    * Specify the Title

    * Select "**Directory** " for the Target 

  * Click "**Next** " and complete all of the required information.

##

PAM **Directory** Record Type Fields

The following table lists all the configurable fields on the PAM Directory
Record Type:

##

PAM Settings and Administrative Credentials

On the "PAM Settings" section of the vault record, you can configure the
KeeperPAM Connection and Tunnel settings and link a PAM User credential for
performing rotations and connections. Tunnels do not require a linked
credential.

###

PAM Settings

Note: PAM User is only required to successfully configure connections and
rotation, and not required for Tunnels.

**Configuration Steps:**

  1. On the PAM Database record, navigate to the PAM Settings section

  2. Select the PAM Configuration and Administrative Credential Record

  3. To configure Keeper Connections and Keeper Tunnels settings, visit the following page:

     1.      2. 

The following screenshot is a PAM Directory Record with LDAPS rotation, RDP
connections and LDAPS tunnels enabled:

# Access Controls

KeeperPAM Access Control Implementation

##

Overview

Access to resources and features in KeeperPAM is governed by a robust cloud-
based access control plane, leveraging multiple layers of policies and
configuration settings. Devices and gateways are assigned specific
permissions, enabling them to access and decrypt data allocated to them from
the vault. Users with KeeperPAM management privileges can assign access rights
to managed resources with flexibility, offering permanent, time-limited, or
just-in-time (JIT) access based on organizational needs.

  *   *   *   *   *   *   *   *   *   * 

###

Planning your Deployment

For optimal use of KeeperPAM, it is recommended to create a dedicated service
account user within the Keeper Admin Console. This account will oversee the
creation and management of Applications, Shared Folders, Gateways, Resources
and their associated rights and permissions.

###

Vault KSM Application Sharing

Keeper Commander and Vault version 17.3+ support "Application Sharing", which
allows multiple administrators to share applications and gateways.

Go to Secrets Manager > Applications > Edit and select the administrators who
require management of the application, devices and gateways.

  * **Application** Admin: Can manage application folders, users, all devices and gateways

  * **Application Viewer** : Can view and use the application and gateways

####

Keeper Commander

Sharing and unsharing applications is available in the Keeper Commander CLI
and SDK.

###

**Role-Based Enforcement Policies**

Enforcement Policies determine what overall permissions a user has associated
to their role. A role can have administrative abilities, or they can be
limited to only using resources assigned to them.

  * From the Admin Console, visit **Admin** > **Roles**

  * Either create a new role or modify an existing role

  * Under Enforcement Policies, visit the "**Privileged Access Manager** " tab

A more in-depth look at Admin Console nodes, roles and permissions can be
found in the Keeper Enterprise admin guide:

  *   * 

###

**PAM Configuration Settings**

The PAM Configuration acts as a set of "parental controls" for PAM records. It
enables or disables specific PAM features for all resources using the
configuration.

  * 

###

Application and Device Access Control

When creating an application with its devices and gateways, the admin assigns
access to specific shared folders with record permissions. This setup allows
controlled vault access for both the gateways and the connected devices
interacting with the Keeper vault. By managing permissions at both the
application and gateway levels, an extra security layer is added.

Multiple applications can be associated to a Shared Folder with different
levels of permission.

###

Device and Gateway IP Locking

When creating a new Device or Gateway on a Windows or Linux-based installation
method, Keeper provides the option to apply IP locking upon first access. This
added security measure is layered on top of the existing device authorization
model.

###

PAM Resource Sharing and Permissions

As a zero-knowledge platform, Keeper provides resource-level access control
through our secure sharing technology, powered by strong encryption. Access to
a resource is controlled through both policy (RBAC, ABAC) in addition to
encryption. In order to access a resource, the user must be able to decrypt
the record in their vault. The decryption process allows the user to establish
a zero trust connection to the target system, or simply access a secret.

In the Keeper Vault, Shared Folders control access to any resource managed by
KeeperPAM. Resources can be placed inside shared folders just like any other
Keeper record.

One of the key benefits of the KeeperPAM platform is the ability to share
access to a resource without exposing credentials to the recipient.

A Shared Folder contains PAM Resources, such as:

  * **PAM Machine**

  * **PAM Database**

  * **PAM Directory**

  * **PAM Remote Browser**

  * **PAM User**

For example, this demo environment as seen below provides full access to
DevOps, but limits access to only viewing and using resources to the
Developers team:

In this scenario, only the DevOps team has access to the Users folder. The
Developers are restricted from accessing these credentials.

####

Record Level Permissions

Resource-level permissions in a shared folder limit members from editing or
sharing records. Users with view-only access can still use PAM features, like
launching sessions, if their role allows it.

To ensure least privilege access, the recommendation is to reduce record-level
permissions in a Shared Folder to "View Only". Only the Keeper service account
user responsible for building Applications and Gateways should have full
administrative capabilities.

####

Direct Resource Sharing

A record can be shared to an individual user with persistent or time-limited
access.

To share an individual record, click on **Share** and then select the user.
Providing view-only access to a resource allows the recipient to launch
connections and tunnels to the target without having access to the underlying
credentials.

A user can be assigned standing access or time-limited access to a resource.

####

Team Level Permissions

From the Admin Console, a team can optionally be restricted in their ability
to edit or re-share records that have been provisioned to the team via shared
folders across the entire environment. This only applies to shared folders
that have been assigned to a specific team.

####

Share Admin Permissions

Managing ownership and permissions of resources and records within the Keeper
Vault can be delegated to other Keeper admins through the Share Admin
permission.

  * 

###

Record Linking

A PAM User record containing credentials can be "linked" to a PAM Resource.
Sharing a PAM Resource record to another user **does not** automatically share
the linked credentials. This allows the recipient with view-only access with
the ability to launch zero-trust connections without having access to the
underlying credentials.

  * Sharing a resource to a user with view-only access only gives them the ability to launch connections and tunnels.

  * 

In the example below, a PAM Database is linked to a specific user `sqluser`.
Connections to the database using that account is available to users without
access to the actual credential.

Here's another example which provides SSH access to a Linux machine without
sharing the key:

###

Time-Limited Access

Folder and record access can be either persistent or time-limited.

Access to the resource can be revoked at a specific date and time.

###

Revoking Access

Removing a user from a Shared Folder or removing the user from a direct share
of the resource will immediately destroy any active sessions or tunnels.

To remove a user from a Shared Folder:

  * Select the Shared Folder

  * Select "Edit" and then remove the user or team from the "Users" tab

  * Click Save

To remove a user from an individual resource

  * Select the record

  * Click on "Sharing"

  * Delete the share

If you select "Remove ... from all your shared records", this will revoke
access to all resources and destroy any active sessions or tunnels for that
user.

###

Automatic Rotation after Share Expiration

If you have a use case where a PAM User credential needs to be shared to
another user, you have the option of automatically rotating the credential
after the sharing has expired.

# Azure Environment Setup

Setting up your Azure environment to work with KeeperPAM

##

Azure Environment Overview

Resources in your Azure environment can be managed by a Keeper Gateway using
Azure App policies and client IDs configured in the PAM Configuration record.

In order to set up your Azure environment, the following steps must be taken:

  * Create an Azure application in the default Azure Active Directory.

  * Get values for the Keeper PAM Configuration from this new application.

  * Grant permissions to the application to access the Azure Active Directory.

  * Create a custom role to allow the application to access/perform actions on various Azure resources.

###

**Create an Azure App Registration**

Go to the **Azure portal** > **Home** and click on **Microsoft Entra ID** on
the left side vertical menu. Select **App Registrations,** and then **New
Registration**. Give the new application a name and select **Single tenant**.
Then click the **Register** button at the bottom.

In the **Overview** of the application, the **Application (client) ID** UUID
is shown. This is the **Client Id** field of the Keeper PAM Configuration
record. The **Directory (tenant) ID** is also shown. This is the **Tenant Id**
field of the Keeper PAM Configuration record. Save these values for later.

Next, click on the **Add a certification or secret** for **Client
credentials**. On the next page, click on New client secret, give the client
secret a Description, and select a desired Expires date, and click **Add**.

The page will refresh showing the secret **Value**. Copy the **Value** (not
Secret ID) into the Keeper PAM Configuration "Client Secret" field. Save this
value for later.

At this point, all the required the PAM Configuration fields should be filled
in. You also have an Azure application that cannot do anything yet.

###

Assign Roles and Administrators

In order for the Azure tenant service principal/application to rotate Azure
Active Directory users or Azure Active Directory Domain Service users, the
application must be a assigned to an Administrative role.

From the Azure portal go to **Home** > **Azure Active Directory** > **Roles
and administrators** , and click on the Administrative role to use (such as
Privileged Authentication Administrator). The correct role depends on what
privileges are needed for your use case. Custom roles can be used.

  * **Global Administrator** \- It is not recommended to use a Global Administrator on a service principal. However, it will allow both administrator and user passwords to be rotated.

  *   * 

To add the application, click **Add assignments** and **Search** for the
service principal/application that was created, click it, and then **Add**.

##

**Assign Azure Role**

Roles need to be attached to the Azure Application (also called a Service
Principle here) in order to rotate passwords of target resources. This is done
in the Subscription section of the Azure portal.

Go to the **Azure portal** > **Home** > **Subscriptions** then select your
subscription. Click on **Access control (IAM)** , and then **Roles**.

Click **Add** on the top menu, and then **Add custom role**. Jump to the
**JSON** tab. Click on **Edit** and paste the JSON object from below,
modifying it according to your setup.

This is a complete list of all of the permissions that Keeper Gateway can use,
if applicable. Only include those that are needed for your setup.

Change the following before you save:

  * <ROLE NAME>: Role Name, e.g. "Keeper Secrets Manager"

  * <DESCRIPTION>: Description, e.g. "Role for password rotation"

  * <SUBSCRIPTION ID>: Subscription ID of this Azure subscription

Click **Save**.

When done, click **Review + create,** and click **Create**.

Once the role is created, it needs to be assigned to the Application (Service
Principle). Click **View** in the **Details** column.

A panel will appear on the right side of the screen. Click **Assignments** ,
and then **Add assignment**.

Enter in the new role's name in the search bar on the **Role** tab, then
double click it to select it. Move to the **Members** tab. Click **Select
members**. In the panel that opens, enter the name of the Azure application,
select the current application, and click **Select**.

Go to the **Review + assign** tab click **Review + assign**.

At this point, you have created the necessary roles and applications within
your Azure environment.

###

PAM Features

The **"PAM Features Allowed"** and **"Session Recording Types Allowed"**
sections in the PAM Configuration allow owners to enable or disable KeeperPAM
features for resources managed through the PAM configuration:

##

Configuring PAM Features on PAM Record Types

After creating the PAM configuration, visit the following pages to:

  *   *   *   *   * 

See  for more info

See  for more info

Ex: `3307=mysql `See  docs

Ex: `192.168.0.15/24` Refer to for more info

See  for more info

See  for more info

Ex: `3307=mysql `See  docs

Ex: `192.168.0.15/24` Refer to for more info

**Required** Visit this  for more details

See

See this  for RDP protocol settings We recommend specifying the **Connection
Port** at a minimum. E.g. "3389" for RDP.

User Accounts can be configured on the PAM User record. Visit this  for more
information.

Learn more about

**Required** Visit this  for more details

See

See this  for SSH protocol settings. We recommend specifying the **Connection
Port** at a minimum. E.g. "22" for SSH.

User Accounts can be configured on the PAM User record. Visit this  for more
information on the PAM User.

PAM Machine records can be shared with other Keeper users within your
organization. However, the recipient must have the  in place to utilize
KeeperPAM features on the shared PAM records.

Learn more about

Connecting to the PAM machine requires only that the Keeper Gateway has access
to the target machine. The Keeper Vault operates independently and does not
require direct connectivity to the machine, leveraging Keeper's zero-trust
network access model to securely manage access through the Gateway. See the
for more details.

**Required** Visit this  for more details

**Required** Visit this  for more details

See

**Required** Visit this  for more details

See

See this  for MySQL protocol settings We recommend specifying the **Connection
Port** at a minimum. E.g. "3306" for MySQL.

User Accounts are configured on the PAM User record. Visit this  for more
information.

Learn more about

**Required** Visit this  for more details

See

See this  for PostgreSQL protocol settings We recommend specifying the
**Connection Port** at a minimum. E.g. "5432" for PostgreSQL.

User Accounts are configured on the PAM User record. Visit this  for more
information.

Learn more about

Connecting to the PAM database requires only that the Keeper Gateway has
access to the database either through native protocols or AWS/Azure APIs. The
Keeper Vault operates independently and does not require direct connectivity
to the database, leveraging Keeper's zero-trust network access model to
securely manage access through the Gateway. See the  for more details.

**Required** Visit this  for more details

See

PAM Record Type

Supported Assets

Field

Description

Notes

PAM Record Type

Supported Assets

Connecting to the protected web application requires only that the Keeper
Gateway has access to the target website. The Keeper Vault operates
independently and does not require direct connectivity to the website,
leveraging Keeper's zero-trust network access model to securely manage access
through the Gateway. See the  for more details.

Field

Description

Notes

Field

Description

Required

Additional information on Remote Browser Isolation is .

extends JIT capabilities to end-user devices, allowing for precise privilege
elevation for specific processes, applications, or tasks without granting full
administrative access.

For more information on specific JIT use cases or implementation guidance,
contact your Keeper Security account manager or email .

Field

Description

Value

Field

Description

Required

User Accounts are configured on the PAM User record. Visit this  for more
information.

Learn more about

PAM Record Type

Supported Assets

Connecting to the PAM Directory requires only that the Keeper Gateway has
access to the target directory service. The Keeper Vault operates
independently and does not require direct connectivity to the service,
leveraging Keeper's zero-trust network access model to securely manage access
through the Gateway. See the  for more details.

Field

Description

Notes

Field

Description

Required

See the  command.

More information on

To ensure least privilege, we recommend splitting the PAM Users into a
separate shared folder, in order to restrict what users and devices can access
the underlying secrets. When launching our  or using our , Keeper will
automatically place the resources and users into separate shared folders.

Read more about the  in the Keeper Enterprise docs

Keeper's  provides access to the target systems without sharing the
credential, ensuring least privilege access.

Next, go to Home > General > Subscriptions and get your subscription ID. Copy
the subscription ID into the Keeper PAM Configuration "Subscription ID" field.
For more information on how to get your subscription ID, visit this .

\- Can change the password for any user, including a Global Administrator
user.

\- Can change the password for any user, except a Global Administrator user.

Field

Description

Configure

Configure

Configure

Configure

Configure

docs

[port mapping](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/references/port-mapping)

[this ](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)

PAM Machine

PAM Database

PAM Directory

PAM Remote Browser

PAM User

docs

[port mapping](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/references/port-mapping)

[this ](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)

Installed and configured the Keeper Gateway

Set up a PAM Configuration for your target Environment

page

Sharing and Access Control

Installed and configured the Keeper Gateway

Set up a PAM Configuration for your target Environment

page

appropriate PAM enforcement policies

Sharing and Access Control

network architecture diagram

Linux Machine

Azure Virtual Machine

Installed and configured the Keeper Gateway

Set up a PAM Configuration for your target Environment

page

Sharing and Access Control

Installed and configured the Keeper Gateway

Set up a PAM Configuration for your target Environment

page

Sharing and Access Control

network architecture diagram

MySQL Database

PostgreSQL Database

Microsoft SQL Server Database

PAM User

Account credential, IAM user, password or SSH Key

PAM Remote Browser

Any http:// or https:// web application, on-prem or in the cloud

URL

IP or Website address

**Required** The target URL only needs to be accessible from the Keeper
Gateway

Title (Required)

Title of the PAM Database Record

`Local SQL Database`

Hostname or IP Address (Required)

Address or RDP endpoint or Server name of the Database Resource

db-mssql-1

Port (Required)

Port to connect to the Database Resource

3306

Use SSL (Required)

Check to perform SSL verification before connecting, if your database has SSL
configured

`Enabled`

Database ID

Azure or AWS Resource ID (if applicable)

**Required** if a managed AWS or Azure Database

Database Type

Appropriate database type from supported databases.

`mssql`

Provider Group

Azure or AWS Provider Group

**Required** if a managed AWS or Azure Database

Provider Region

Azure or AWS Provider Region

**Required** if a managed AWS or Azure Database

PAM Directory

Active Directory, OpenLDAP

Hostname or IP Address

Address of the directory resource

**Required**

Port

Port to connect on

**Required** Typically **389** or **636**(LDAP/LDAPS) Active Directory only
supports 636

Use SSL

Use SSL when connecting

Required for Active Directory

Alternative IPs

List of failover IPs for the directory, used for Discovery

Newline separated

Directory ID

Instance ID for AD resource in Azure and AWS hosted environments

**Required** if Azure Active Directory or AWS Directory Service AWS Example:
"d-9a423d0d3b'

Directory Type

Directory type, used for formatting of messaging

**Required** Must be **Active Directory** or **OpenLDAP**

User Match

Match on OU to filter found users during Discovery

Domain Name

domain managed by the directory

**Required** Example: `some.company.com`

Provider Group

Provider Group for directories hosted in Azure

**Required** for directories hosted in Azure

Provider Region

AWS region of hosted directory

**Required** for directories hosted in AWS Example: `us-east-2`

EC2 Role Policy

IAM User Policy

Copy

    
    
    {
        "properties": {
            "roleName": "<ROLE NAME>",
            "description": "<DESCRIPTION>",
            "assignableScopes": [
                "/subscriptions/<SUBSCRIPTION ID>"
            ],
            "permissions": [
                {
                    "actions": [
                        "Microsoft.Compute/virtualMachines/read",
                        "Microsoft.Network/networkInterfaces/read",
                        "Microsoft.Network/publicIPAddresses/read",
                        "Microsoft.Network/networkSecurityGroups/read",
                        "Microsoft.Compute/virtualMachines/instanceView/read",
                        "Microsoft.Resources/subscriptions/resourceGroups/read",
                        "Microsoft.AAD/domainServices/read",
                        "Microsoft.Network/virtualNetworks/subnets/read",
                        "Microsoft.Sql/servers/read",
                        "Microsoft.Sql/servers/databases/read",
                        "Microsoft.DBforPostgreSQL/servers/read",
                        "Microsoft.DBforMySQL/servers/read",
                        "Microsoft.DBforPostgreSQL/servers/databases/read",
                        "Microsoft.Sql/servers/write",
                        "Microsoft.DBforPostgreSQL/servers/write",
                        "Microsoft.DBforMySQL/servers/write",
                        "Microsoft.DBforMySQL/flexibleServers/read",
                        "Microsoft.DBforPostgreSQL/flexibleServers/read",
                        "Microsoft.DBforPostgreSQL/flexibleServers/write",
                        "Microsoft.DBforMySQL/flexibleServers/write",
                        "Microsoft.DBforMariaDB/servers/read",
                        "Microsoft.DBforMariaDB/servers/write"
                    ],
                    "notActions": [],
                    "dataActions": [],
                    "notDataActions": []
                }
            ]
        }
    }

Rotation

If enabled, allow rotations on privileged user users managed by this PAM
configuration

Connections

If enabled, allow connections on resources managed by this PAM configuration

Remote Browser Isolation (RBI)

If enabled, allow RBI sessions on resources managed by this PAM configuration

Tunneling

If enabled, allow tunnels on resources managed by this PAM configuration

Graphical Session Recording

If enabled, visual playback sessions will be recorded for all connections and
RBI sessions

Text Session Recording (TypeScript)

If enabled, text input and output logs will be logged for all connections and
RBI sessions

Local Network

AWS

Azure

Domain Controller

this section

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[section](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections/session-protocols/rdp-connections)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[section](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections/session-protocols/ssh-connections)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[section](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections/session-protocols/mysql-connections)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[section](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections/session-protocols/postgresql-connections)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

network architecture diagram

[available at this
page](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[Keeper Privilege
Manager](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/endpoint-privilege-
manager/overview)

[Keeper Privilege
Manager](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/endpoint-privilege-
manager/overview)

[Password Rotation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/password-rotation)

[pam@keepersecurity.com](mailto:pam@keepersecurity.com)

Installed and configured the Keeper Gateway

Set up a PAM Configuration for your target Environment

page

Sharing and Access Control

network architecture diagram

[Keeper
Connections](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections)

[Keeper Tunnels](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/tunnels)

[Nodes and Organizational Structure](https://docs.keeper.io/en/enterprise-
guide/nodes-and-organizational-structure)

[Roles, RBAC and Permissions](https://docs.keeper.io/en/enterprise-
guide/roles)

PAM Configuration

[Quick Start
Sandbox](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/quick-start-sandbox)

Gateway wizard

[Share Admin feature](https://docs.keeper.io/en/enterprise-
guide/sharing/share-admin)

zero-trust architecture

[page](https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-
tenant-id)

[**Privileged Authentication Administrator**](https://learn.microsoft.com/en-
us/azure/active-directory/roles/permissions-reference#privileged-
authentication-administrator)

[**Authentication Administrator**](https://learn.microsoft.com/en-
us/azure/active-directory/roles/permissions-reference#authentication-
administrator)

[Rotation](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/password-rotation)

[Connections](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/connections)

[RBI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[Tunnels](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/tunnels)

[Discovery](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/discovery)

section

Planning your Deployment

Role-Based Enforcement Policies

PAM Configuration Settings

Application and Device Access Control

Device and Gateway IP Locking

PAM Resource Sharing and Permissions

Record Linking

Zero-Trust Access through Connection Sharing

Time-limited Access

Revoking Access

Login

**Required** Examples:****`username` `username@domain` `DOMAIN\username`

Password

Password of the user

Can be rotated

Private PEM Key

PEM Key associated with user

Can be rotated

Distinguished Name

Distinguished name; used if associated with a PAM Directory

**Required** only when the User is managed by a directory **** Example:
CN=Jeff Smith,OU=Sales,DC=demo,DC=COM

If left blank, defaults are attempted depending on the provider type

Managed User

Flag for accounts that are managed by the AWS or Azure IAM systems

Set by Keeper Discovery to indicate that the password cannot be rotated. For
example, AWS token-based auth.

Connect Database

Used in certain scenarios if a database name is needed

Edge cases, e.g. using LDAP to connect to a MySQL database

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required**

Browser Autofill Credentials

Linked PAM User credential used for autofill

Protocol

Native protocol used for connecting from the Gateway to the target

**Required**

Session Recording

Options for recording sessions and typescripts

Browser Settings (multiple)

Browser-specific protocol settings

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required -** This is the PAM configuration you created in the prerequisites

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

Protocol

Native database protocol used for connecting from the Gateway to the target

**Required -** for this example: "SQL Server"

Session Recording

Options for recording sessions and typescripts

Connection Parameters

Connection-specific protocol settings which can vary based on the protocol
type

PAM Configuration

Associated PAM Configuration record which defines the environment

**Required**

Administrative Credential Record

Linked PAM User credential used for connection and administrative operations

**Required**

Protocol

Native protocol used for connecting the session from the Gateway to the target

**Required**

Session Recording

Options for recording sessions and typescripts

Connection Parameters (multiple)

Connection-specific protocol settings which can vary based on the protocol
type

Depends on protocol. We recommend specifying the **Connection Port** at a
minimum.

Username; exact context and format depends on the associated resource. See
below.

See

See

**Required** Visit this  for more details

See

See this  for SQL Server protocol settings We recommend specifying the
**Connection Port** at a minimum. E.g. "**1433** " for SQL Server.

See

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[RBI page](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/remote-browser-isolation)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[section](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/connections/session-protocols/mysql-connections)

[session recording](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/session-recording-and-playback)

[Keeper Commander](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-
cli/command-reference/reporting-commands)

###

Connecting to the Host Instance

A very useful capability of the Keeper Gateway is being able to open
connections and tunnels to the host machine. By adding the `extra_hosts`
section to your docker compose file with a value of
`host.docker.internal:host-gateway`, you can open sessions directly to the
host.

Example docker compose with the Gateway container:

Copy

    
    
    services:
          keeper-gateway:
            platform: linux/amd64
            image: keeper/gateway:latest
            shm_size: 2g
            restart: always
            extra_hosts:
              - "host.docker.internal:host-gateway"
            security_opt:
              - "seccomp:docker-seccomp.json"
            environment:
              ACCEPT_EULA: Y
              GATEWAY_CONFIG: xxxxxxxx

Enabling this option allows you to establish a Connection to the host. For
example, to open an SSH connection:

  *   *   * 

###

Upgrading the Keeper Gateway service through the host

If you use KeeperPAM to SSH over to the host service, you can upgrade the
container by running the container update of the gateway in the background:

Copy

    
    
    docker-compose pull
    nohup docker-compose up -d keeper-gateway &

Create a  record with the SSH private key

Create a  record with the hostname to `host.docker.internal` and port `22`

Activate the  in PAM settings referencing the PAM User

PAM User

PAM Machine

[SSH connection](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-
access-manager/connections/session-protocols/ssh-connections)

[page](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/master)

###

Checksum Verification

Keeper Gateway SHA256 hashes for the latest version are published at the below
location:

Calculating and verifying the checksum:

####

Linux

Copy

    
    
    sha256sum keeper-gateway_linux_x86_64
    cat keeper-gateway_X.X.X_SHA256SUMS | grep keeper-gateway_linux_x86_64

####

PowerShell

Copy

    
    
    Get-FileHash -Algorithm SHA256 keeper-gateway_windows_x86_64.exe | Format-List
    Get-Content keeper-gateway_X.X.X_SHA256SUMS | Select-String keeper-gateway_windows_x86_64.exe

###

Checksum Verification

Keeper Gateway SHA256 hashes for the latest version are published at the below
location:

Calculating and verifying the checksum:

####

Linux

Copy

    
    
    sha256sum keeper-gateway_linux_x86_64
    cat keeper-gateway_X.X.X_SHA256SUMS | grep keeper-gateway_linux_x86_64

####

PowerShell

Copy

    
    
    Get-FileHash -Algorithm SHA256 keeper-gateway_windows_x86_64.exe | Format-List
    Get-Content keeper-gateway_X.X.X_SHA256SUMS | Select-String keeper-gateway_windows_x86_64.exe

<https://keepersecurity.com/pam/latest.txt>[](https://keepersecurity.com/pam/latest.txt)

<https://keepersecurity.com/pam/latest.txt>[](https://keepersecurity.com/pam/latest.txt)

On the "Rotation Settings" section of the PAM User vault record, you can
configure how credential rotation is managed.

###

Password Rotation Settings

Field

Description

Required

Rotation Type

Specifies which type of rotation is being performed (and which protocol is
utilized).

**Required** "General", "IAM User" or "Run PAM Scripts Only". See below for
details.

PAM Resource

For General rotation type, specifies the PAM Resource record which can provide
the necessary privilege. For IAM User rotation type, specifies the PAM
Configuration utilizing cloud APIs.

**Required** only for "General" and "IAM User" rotation types

Rotation Schedule

Rotation can be performed on-demand or on a specific schedule.

Password Complexity

Applies to password-based rotations, not PEM keys.

Select "Show More" to control special characters and symbols.

###

Rotation Type

Keeper supports 3 different types of rotation:

  * **General:** Uses native protocols for performing the rotation, such as LDAP, Databases, SSH keys, etc.

  * **IAM User:** Uses the cloud-specific APIs for performing rotation, such as AWS IAM users and Azure managed resources. In this case, only the PAM Configuration is required since it contains the necessary 

  * **Run PAM scripts only:** Skips the standard rotation and only executes the attached PAM Scripts.

###

PAM Resource

To complete the Rotation setup, you need to select a resource, which depends
on the rotation type.

For a "General" rotation, the Keeper Gateway uses a native protocol for
performing the necessary rotation, and the rotation will be executed on the
associated PAM Resource supplied. If necessary, the rotation will use the
associated administrative credential on the PAM Resource.

In the example below, a Windows service account password is going to be
rotated on the associated Windows Server.

For an "IAM User" rotation type, the Keeper Gateway will use the referenced
PAM Configuration to determine which APIs and methods are used to perform the
rotation. In the example below, an IAM user in AWS will use the "AWS (US-
WEST-1)" configuration.

When using the IAM User rotation method, it is assumed that the Keeper Gateway
either inherits its privilege from the instance role policy, or through
explicit access keys that are provided on the PAM Configuration record.

###

In Summary:

  * The PAM User record holds the credential that is being rotated.

  * The Rotation Settings of the PAM User record references a specific PAM Machine, PAM Database or PAM Directory resource. This is the target resource where the rotation is performed.

  * The Keeper Gateway uses the Admin Credential associated to the PAM Machine, PAM Database or PAM Directory resource to perform the rotation with native protocols.

  * For AWS and Azure managed resources, Keeper uses Instance Role permission of the Gateway, or specific PAM Configuration secrets to perform the rotation with APIs.

###

Examples

Below are some examples of PAM User records.

  * Windows Domain Admin

  * Windows Domain User with post-rotation scripts

  * AWS IAM User

  * Database user

  * Azure AD User

For advanced scheduling, see the .

The rotation schedule can be set on a specific interval, or using a .

[cron spec](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/references/cron-spec)

[cron spec](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/privileged-access-
manager/references/cron-spec)

this section

[MSP Consumption Model](https://docs.keeper.io/en/enterprise-guide/keeper-
msp/consumption-based-billing)

[Secure Add-On](https://docs.keeper.io/en/enterprise-guide/keeper-
msp/consumption-based-billing/secure-add-ons)

[Reporting, Alerts & SIEM integration](https://docs.keeper.io/en/enterprise-
guide/event-reporting)

[Time-Limited Access](https://docs.keeper.io/en/enterprise-guide/sharing/time-
limited-access)

[15KBdocker-
seccomp.json](https://762006384-files.gitbook.io/~/files/v0/b/gitbook-x-
prod.appspot.com/o/spaces%2F-MJXOXEifAmpyvNVL1to%2Fuploads%2FMjBgU5aJYkp8Em3ZV9OD%2Fdocker-
seccomp.json?alt=media&token=73227956-f299-47e5-80aa-764ea2ab9e93)

PAM User record editing

Password Rotation Settings

Custom Schedule

Calendar Settings

Cron Spec

Rotation Resource

IAM User rotation type

Windows Domain Admin User

Windows Domain User with post-rotation scripts

AWS IAM User

Database user

Azure AD User

KeeperPAM Architecture

Typical Folder Setup for KeeperPAM

Linked Credentials in the Users folder

Human users with access to a Shared Folder

Applications and Machines with access to a Shared Folder

Secrets Manager Applications

Devices

Keeper Gateway

PAM Configuration

Creating a PAM Resource

PAM User linked to PAM Resource

PAM User settings

One-Time Access Token

Managing Applications

Creating a Shared Folder

Add Application to Shared Folder

Assigning a Gateway to an Application

Create a Gateway and associated applications

Gateway Creation Wizard

Splitting Resource and Credentials

Finish Record Splitting

Converted Resource with Split Credential

Create a Device

Add a device using One-Time Access Token and IP Lockdown

Access Token Generated

Creating a new device with Configuration File method

Device created with Configuration method

Docker Logs from Keeper Gateway

Gateway is Online

Creating a Gateway

Create a KSM Application

Windows Gateway

Keeper Gateway for Windows

Service Account Setup

Keeper Gateway Service

Verbose Logging Mode

Select Configuration Method

Copy the Base64 Configuration

Create Secret using Plaintext formatting

Secret Name and Description

View Secrets

KeeperPAM Events

Set Alert for Gateway Offline

Gateway Offline Alert

Email Alert for Gateway Offline

Windows Automatic Updates

Create a new PAM Resource Record

Right-click to create PAM Resource Records

Selecting a Target

AWS Rotation Hierarchy

Example of Azure Windows VM

Linux Machine Example

Creating a new PAM Machine record

PAM Settings and Administrative Credentials

PAM Settings for a PAM Machine resource

PAM Machine Record - Windows

PAM Machine Record - Linux

PAM Database

Administrative Credential Record

Sharing PAM Database Records

MySQL Database Record

Connection to MySQL Database

MySQL Interactive Session

PostgreSQL PAM Database Record

Administrative Credential Record

Sharing a PostgreSQL Database Record

Launching interactive CLI session to PostgreSQL

Interactive Connection to PostgreSQL Database

Create a PAM Database

PAM Settings and Administrative Credentials

PAM Settings on Database resource

PAM Database with Connections and Tunnels activated

Creating a PAM User

Creating a Browser Isolation Record

PAM Settings on a Remote Browser Isolation resource

PAM Settings for Remote Browser Isolation

Autofill Credentials for Remote Browser Isolation

PAM Remote Browser resource

Just-In-Time Ephemeral Account Creation during PAM Sessions

Just-In-Time Role Elevation during Privileged Sessions

Just-In-Time Access with Keeper Privilege Manager

Time-Limited Access

Workflow and Requests for Approval

SQL Server PAM Database Record

Administrative Credential Record

Sharing PAM Database Records

Microsoft SQL Server Database

Connection to a Microsoft SQL Database

Interactive Session with Microsoft SQL Database

Creating a PAM Directory

PAM Settings

PAM Settings

PAM Directory with Connection, Rotation and Tunnel Enabled

Application Sharing

PAM Roles

Example of role with KeeperPAM administration capabilities

Example of a role with the ability to only launch connections and tunnels

PAM Configuration

Application Permissions

Adding multiple applications to a shared folder

Device and Gateway IP Locking

Managing access to PAM Resources

Managing access to PAM Users

Record-level permissions on PAM Resources

Share an Individual Resource

Sharing with Time-limited Access

Restricting Permissions on Teams

Share Admin Permissions

Linking a PAM User to a Resource

SSH Access to a machine without the key

Time-limited Access

Removing access

Rotate password upon expiration

Create Application

Client Secret

Assign Administrator Role to Keeper Application

Role

Create Azure Custom Role

Assign Role to Keeper Secrets Manager application member

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FOXi2mFqCpWzFOEFamNfS%252FScreenshot%25202025-01-23%2520at%25204.33.26%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D5fdba450-37b9-4cf8-9ecb-f9ce341948c3&width=768&dpr=4&quality=100&sign=81556070&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F5nWthY6PzkuyCPswOm1g%252FScreenshot%25202025-01-14%2520at%25209.42.30%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db0fffa2c-42ee-4f11-97de-b37e14d56924&width=768&dpr=4&quality=100&sign=6c560da4&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FTmiv0hvl0miQxomi0CnG%252FScreenshot%25202025-01-14%2520at%25209.50.46%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dfd5381d6-f451-4f2a-8e46-c4cab48e3b47&width=768&dpr=4&quality=100&sign=299f5b7f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F0he1Hr0prQpo7N7GqIZ3%252FScreenshot%25202025-01-14%2520at%25209.50.56%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dfc6b40d7-0612-415d-b029-8df7d6ba3d1e&width=768&dpr=4&quality=100&sign=9f8dda08&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F4y6jRZ4RfZ7fDm0KQN3Y%252FScreenshot%25202025-01-14%2520at%25209.51.03%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db4e3104e-b14e-462d-84e2-2b19e946b9ed&width=768&dpr=4&quality=100&sign=7e42fc60&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F8OB6YiUox2fAgFUgyNWv%252FScreenshot%25202025-01-23%2520at%25206.13.23%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dfe9db3bc-0e29-4734-9778-3f2fb1c14783&width=768&dpr=4&quality=100&sign=e2a7fb32&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F06v6s4b2EYgJJhux1s2N%252FScreenshot%25202025-01-23%2520at%25206.14.34%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D9ae719fc-b73d-406c-9c25-6cd0b2ee9778&width=768&dpr=4&quality=100&sign=4f23bfc3&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F29D3LswWwgW5pvSOMUMl%252FScreenshot%25202025-01-12%2520at%25207.16.05%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D01c3c45f-518a-4ca5-b198-723ff0f1a227&width=768&dpr=4&quality=100&sign=347fdad0&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FUBcUVVRpqUFzjfXGUd47%252FScreenshot%25202025-01-14%2520at%25209.32.50%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Da49d938d-f2b3-420a-9cdb-301ea9b9a1ad&width=768&dpr=4&quality=100&sign=5315228a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FvL1pNfWvzwMfSUbfG6oA%252FScreenshot%25202025-01-12%2520at%25207.17.12%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D975b84a9-26a5-4040-b193-bbd90e272827&width=768&dpr=4&quality=100&sign=e53e4e6a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FwQ8O48hEFY00feefNoI4%252FScreenshot%25202025-01-12%2520at%25207.17.32%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Df4ecf7da-2231-4dd7-902e-80a57cbadb52&width=768&dpr=4&quality=100&sign=9ff95515&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGzKgObBvzWPED5PdcznT%252FScreenshot%25202025-01-12%2520at%25207.18.52%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D393cb4c4-0d1f-44ad-
bc09-fc66a93e666f&width=768&dpr=4&quality=100&sign=e3dbf592&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9IDMEosXrorfBpUMnr22%252Fkeeperpam-
system-
architecture.jpg%3Falt%3Dmedia%26token%3D9afb26d1-5da9-4834-8bba-2366035cc267&width=768&dpr=4&quality=100&sign=8e135273&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FS3qT4Avm5vAU5DlEYPBE%252FGetting%2520Started.jpg%3Falt%3Dmedia%26token%3D8fbdc83a-6ac8-4ae9-8036-0b57c1307745&width=768&dpr=4&quality=100&sign=bd5d513b&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FHAQZMfu5ZSg6QAGqOJiF%252FEnforcement%2520Policies.jpg%3Falt%3Dmedia%26token%3D926aec64-b51a-4117-9f66-6e47da3f221b&width=768&dpr=4&quality=100&sign=ec40800c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FaQ7p5RLxwdds2EuRh3xi%252FVault%2520Structure.jpg%3Falt%3Dmedia%26token%3D0e679b03-50b6-4717-b44f-726831228e91&width=768&dpr=4&quality=100&sign=75ab8418&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FCtsat1SwQFigsikiCd47%252FScreenshot%25202024-12-26%2520at%252011.38.04%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D0132deb6-8b9c-4cc9-ac29-82873b0acde8&width=768&dpr=4&quality=100&sign=d559afca&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FxBYTGFGA7ABzxAOnhJcG%252FScreenshot%25202024-12-26%2520at%252011.41.33%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D2a13336a-00ae-40c5-942e-11e8edb04321&width=768&dpr=4&quality=100&sign=69d1cb51&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FkJkYFLs5JXayhx3nCS3W%252FScreenshot%25202024-12-26%2520at%252011.46.53%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db720c477-c17b-4275-a595-107d85125ca3&width=768&dpr=4&quality=100&sign=c2ca32d&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F8Zd9N5ubtJResaTju33Q%252FScreenshot%25202024-12-26%2520at%252011.53.32%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D5700f75b-c640-4478-9329-26e3ae45e973&width=768&dpr=4&quality=100&sign=6b8f745f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FuOSr5TUItvs4QtafVXeJ%252FScreenshot%25202024-12-26%2520at%252011.52.10%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Da629a8e0-d325-4564-bbea-a2185ee8cc63&width=768&dpr=4&quality=100&sign=3848f147&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FfsgmSxfTlrc4RxdTqt7i%252FScreenshot%25202024-12-26%2520at%252012.57.19%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D161238df-7e7c-426a-96da-3956695d606c&width=768&dpr=4&quality=100&sign=b751dc78&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FjxAxzWoNkwTk3Mx35mXC%252FScreenshot%25202024-12-26%2520at%25201.04.39%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Daf2b8bd1-7e69-4a6a-a4b0-3fa1b5b068c1&width=768&dpr=4&quality=100&sign=54d5c314&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FNIKgp1VaCP1zqf23quiX%252FScreenshot%25202024-12-26%2520at%25201.07.23%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D0106e8a1-c8a7-4701-87d9-44cdeb5cd684&width=768&dpr=4&quality=100&sign=e8b04c3b&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FCHjkisV0JQqAi4SGGuhJ%252FScreenshot%25202024-12-26%2520at%25201.12.49%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Df3459046-53ec-4ed8-b5fa-88ba8d14968b&width=768&dpr=4&quality=100&sign=5766b81b&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FqIWFAJ4zlwyOP0afYDuM%252FScreenshot%25202024-12-26%2520at%25201.52.00%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D2f3ce88d-4ecc-404c-9c73-05e575114ba3&width=768&dpr=4&quality=100&sign=2b0860ca&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FCIJ4xtf2Tqt36mIKdi36%252FScreenshot%25202024-12-26%2520at%25201.54.39%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D842c51df-2a6e-4486-b774-440c4c9ee5af&width=768&dpr=4&quality=100&sign=3cd51e70&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FuUwDOjhl0r67wyzFe4wc%252FScreenshot%25202024-12-26%2520at%25201.53.33%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D62dfded2-1db2-4075-9fa9-8c5a5f95bc67&width=768&dpr=4&quality=100&sign=e69a750d&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FlGKhrtW3C17QpVPL2y1U%252FApplications.jpg%3Falt%3Dmedia%26token%3D3a9db568-10db-414c-a954-ec26f8b66dc9&width=768&dpr=4&quality=100&sign=8ecfa768&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F7c4Wl59Aw89PNoAh2jqH%252FScreenshot%25202024-12-26%2520at%25207.04.55%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D6283ebab-
de8d-49d7-b12c-4933c7e68a20&width=768&dpr=4&quality=100&sign=3b0cca74&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fxd8DfE0CZZHJz6L6fQul%252FScreenshot%25202024-12-26%2520at%25207.05.15%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D934afd24-1594-48eb-a80c-d859d40e419e&width=768&dpr=4&quality=100&sign=993a8ab0&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FrGAwVXeftS4nvxQgyt0c%252FScreenshot%25202024-12-26%2520at%25207.05.39%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D63128e5b-44d9-4cb1-86e6-d4251ae3d10f&width=768&dpr=4&quality=100&sign=b7b2c88a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FmoLDmyO7KrkidzqaItHt%252FScreenshot%25202024-12-26%2520at%25207.07.40%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D961bbddf-b14a-4d82-a0f7-9277548deb51&width=768&dpr=4&quality=100&sign=81766c5e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fj52SOKVTh70KYp2hY5m3%252FScreenshot%25202024-12-26%2520at%25207.08.09%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dd08bcd35-0807-4f66-8c2e-d87da108d34f&width=768&dpr=4&quality=100&sign=b6e2b076&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FuurHOOWU1OArMPW26bov%252FScreenshot%25202024-12-26%2520at%25207.21.31%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dd09b8ae9-f50f-455d-acd2-4b33947c6c64&width=768&dpr=4&quality=100&sign=e71a85c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FMhDrfJxtwD5BfXTzW30Y%252FScreenshot%25202024-12-26%2520at%25207.25.56%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Ddf02b30a-eccb-4df2-9ecf-
dc726ed6da4c&width=768&dpr=4&quality=100&sign=1a21cd7f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FD8CTwQzk8HCmJnqzuxac%252FScreenshot%25202024-12-26%2520at%25207.26.16%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D6fd67625-7400-4857-8a6f-b02874a46f6c&width=768&dpr=4&quality=100&sign=1e38b3ec&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FBylph24gZsEZmL0kHBTH%252FScreenshot%25202025-01-11%2520at%25203.34.59%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D9017a9f3-6d8f-4444-be1a-5c53593496e8&width=768&dpr=4&quality=100&sign=86c93d48&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGkuvoAJeMsLvZr8rCfTk%252FScreenshot%25202025-01-11%2520at%25203.35.49%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3De043eebe-b0f9-4c28-95cf-28add79c0976&width=768&dpr=4&quality=100&sign=29094312&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FF2dQCWCBYPAJF0gm0uok%252FScreenshot%25202025-01-11%2520at%25204.37.32%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3De329168c-71db-41b3-8ae8-d53aa7ab8d28&width=768&dpr=4&quality=100&sign=60b9ab59&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FakdhgZ76MX49kJJbPScK%252Fgateway.jpg%3Falt%3Dmedia%26token%3Db511fac0-f22f-4b6c-a362-d8dc86272e5c&width=768&dpr=4&quality=100&sign=ff08947&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F5ftStQCAmP0Ff6YRT1hO%252FDevices.jpg%3Falt%3Dmedia%26token%3Dcc7439f2-e1e5-4755-be90-d4782bb1923f&width=768&dpr=4&quality=100&sign=a7e9b756&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FvXs6AeY5tmdvIyzQ8gWv%252FScreenshot%25202024-12-26%2520at%25207.59.36%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D611bfb73-e966-40db-
bd44-962eb1fcc59c&width=768&dpr=4&quality=100&sign=3256c230&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F4W35bPtAymO4Sbx27Qwg%252FScreenshot%25202024-12-26%2520at%25208.00.25%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D4424ce27-486f-40eb-
ad4c-ec67fa219354&width=768&dpr=4&quality=100&sign=ff819562&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FOuI8qji19fOvDvdMLAUI%252FScreenshot%25202024-12-26%2520at%25208.01.32%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Da06c0903-78ba-42a8-bb7c-e3970298b118&width=768&dpr=4&quality=100&sign=ee435d61&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FpfSN89i3gEWOSpOMWCDS%252FScreenshot%25202024-12-26%2520at%25208.00.36%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D8d5dc364-f8f3-47a4-9e21-81ae4a006f38&width=768&dpr=4&quality=100&sign=2a72e6a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F14KWP5B9HsqwWDW1GRIs%252FScreenshot%25202024-12-26%2520at%25208.01.55%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D9c104dad-d333-49ef-9491-a27af0e79423&width=768&dpr=4&quality=100&sign=8eca1129&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FZdCwOSIZ90eIqXaHSQ7N%252FDocker%2520Install.jpg%3Falt%3Dmedia%26token%3D577af308-2d82-4423-8d62-a94826e60bc6&width=768&dpr=4&quality=100&sign=8bebeb77&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FuLk5SZEF58TniLsYGKII%252FScreenshot%25202024-12-27%2520at%25209.29.10%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3De9a6d790-80d2-4bdc-8ebe-a08cd88119a5&width=768&dpr=4&quality=100&sign=c202035e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FpdccmtxqPQDtpeTrL7gh%252FScreenshot%25202024-12-27%2520at%25209.38.24%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D3c64598f-c12e-4e6a-9fa9-9a948c605397&width=768&dpr=4&quality=100&sign=bd809e33&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FrperdEulgHMqKZAh4itn%252FScreenshot%25202025-04-19%2520at%25207.46.13%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dfcadc16c-003b-46f2-b6b7-8666d91c27a2&width=768&dpr=4&quality=100&sign=24efc03d&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGfrKhg3EYK2mAtfmsq1x%252FScreenshot%25202023-05-01%2520at%252011.37.56%2520AM.jpg%3Falt%3Dmedia%26token%3D21236241-e0f2-4b54-b7dd-9f3cea8ab53c&width=768&dpr=4&quality=100&sign=2355f5&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FJKAv2CyVdxhUf7m7k7TY%252FScreenshot%25202023-09-14%2520at%25205.46.20%2520PM.png%3Falt%3Dmedia%26token%3Db1b3336b-b34d-4faa-
aa75-1b5f54170233&width=768&dpr=4&quality=100&sign=8097b719&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FLrkXCEAnkZ5mHSvXvqLE%252FLinux%2520Install.jpg%3Falt%3Dmedia%26token%3D132b3ef1-e943-461b-8c25-753ccce83a38&width=768&dpr=4&quality=100&sign=50ec59bd&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FMKUPFqx5R4qNbP4UvDEA%252FWindows%2520Install.jpg%3Falt%3Dmedia%26token%3Da0bae005-cca1-4d63-9ab2-0c36c06b48b2&width=768&dpr=4&quality=100&sign=846876de&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FEmNFPFH1OL9YhIvTMxzz%252FScreenshot%25202025-02-14%2520at%25204.47.50%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D8e76ef63-658a-43fd-
ab99-f7b8b89bdaf5&width=768&dpr=4&quality=100&sign=14a907d2&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FIoAEQf7xnRCENtcZN8XF%252FwindowsInstaller%25232.png%3Falt%3Dmedia%26token%3D6d330e57-ec06-4fb5-a450-66e9f2db3e8a&width=768&dpr=4&quality=100&sign=a802bd49&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9IAdgaW9qb5yXpZF5Cj3%252FwindowsInstaller%25233.png%3Falt%3Dmedia%26token%3De53521b5-8f18-4de3-ae52-faa0c9dc105d&width=768&dpr=4&quality=100&sign=ee065984&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FRPmmLYEln37uzuhGJnK1%252FScreenshot%25202025-02-14%2520at%25204.54.23%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D45d2a0bd-c544-4c8f-a0bb-37b1acab87ba&width=768&dpr=4&quality=100&sign=388ba355&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FNqfhdJpjRCJbgs6RfYjP%252Fimage.png%3Falt%3Dmedia%26token%3D88ee8691-e886-48b8-99ec-1e2ff1fe4f6c&width=768&dpr=4&quality=100&sign=aa608a9c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FAe5xYSWFNfKaxrHnMvJt%252FScreenshot%25202024-12-31%2520at%25202.46.15%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D55ae2ada-7f86-4d72-aa87-18a61bfdc6d7&width=768&dpr=4&quality=100&sign=cd7223c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F6Mj7hQtyDXndJOJLtkN6%252FScreenshot%25202024-12-31%2520at%25202.32.57%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D319b654d-3886-4815-a683-64e863b1326b&width=768&dpr=4&quality=100&sign=b296cd5f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FXEvlscEMXs84Fbz5lAXD%252FScreenshot%25202024-12-31%2520at%25202.33.08%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D124b08ef-324d-47c1-9ab5-49c49b773713&width=768&dpr=4&quality=100&sign=b74489ef&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FBF7NV7ChEZYjpcJTJ4oI%252FScreenshot%25202024-12-31%2520at%25204.00.36%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Ddcff8b26-fcca-42d1-9162-ec7e9a0536f3&width=768&dpr=4&quality=100&sign=c204d91c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FCDLKSG2dxlkp8VcnZ0lG%252FScreenshot%25202024-12-31%2520at%25202.57.58%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D8a0af639-718d-464d-99d9-3639d5521c2e&width=768&dpr=4&quality=100&sign=78e7d3f6&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F58kXg5tcowhN2UJNwtvU%252FScreenshot%25202024-12-31%2520at%25202.59.36%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D88b21981-79eb-462d-b41d-b49fd591d42b&width=768&dpr=4&quality=100&sign=9b3cbef3&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F7HKEvnUmuwxtqzWrtAEH%252FScreenshot%25202025-02-22%2520at%25205.52.13%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D317f6374-5d64-4e14-9f35-14a73822541c&width=768&dpr=4&quality=100&sign=355aa33a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FCTid6ZraCYRFA0ZppXsp%252FScreenshot%25202025-02-22%2520at%25206.49.59%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D72c05446-21cc-41d5-9afb-b9e82be1de2e&width=768&dpr=4&quality=100&sign=b6a77551&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F3dh5GtgJnyDtzJ0hjTfS%252FScreenshot%25202025-02-22%2520at%25206.47.09%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Db298b1d3-c69a-40b8-b14a-2ac845ac79a5&width=768&dpr=4&quality=100&sign=65e20a70&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FJI6cxiJgIuhgFKkkKuYV%252FScreenshot%25202025-02-23%2520at%25207.43.17%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dccf0ad22-a732-430a-b206-5b7d36df3cb6&width=768&dpr=4&quality=100&sign=e80cc5c5&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FIVb77fSHLENBCICa4kGc%252Fimage.png%3Falt%3Dmedia%26token%3Da74167f2-c46c-4548-bf82-1a44ab719539&width=768&dpr=4&quality=100&sign=5894a0eb&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9R0nfNJVPTwAkHePdcaP%252Fimage.png%3Falt%3Dmedia%26token%3D649c4117-2e17-40c8-a07e-66624d411c19&width=768&dpr=4&quality=100&sign=bff8be29&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fz58USWZNQlLP5Alvonau%252Fimage.png%3Falt%3Dmedia%26token%3D1c645547-8a96-45a0-badb-7ebd2803ff03&width=768&dpr=4&quality=100&sign=3590994f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F8BFeFROeVqmC8KhlQPZL%252Fimage.png%3Falt%3Dmedia%26token%3D27c9dfc8-a8a7-4b83-877f-7a638cd5b710&width=768&dpr=4&quality=100&sign=5f7dd22&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FTEpWJKKgJos84Q5jNeZS%252Fimage.png%3Falt%3Dmedia%26token%3D5248f4c6-c27f-41cd-830e-63542633c63e&width=768&dpr=4&quality=100&sign=e3507b53&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FtnIDbstjLAfq2ECqq9HB%252FScreenshot%25202024-12-28%2520at%25203.01.48%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3De63d20a1-aa96-4fbd-89ed-d0fdd455a830&width=768&dpr=4&quality=100&sign=28fcb001&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FMeo2Pl0F5xDl8iY2NQeK%252FScreenshot%25202024-12-28%2520at%25203.05.53%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D811e735e-6692-4f26-88a7-4e4e02bd2ec4&width=768&dpr=4&quality=100&sign=a57a48e6&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FNqfGO32FajbD2yVagIb5%252FScreenshot%25202024-12-28%2520at%25203.01.06%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Df2ba3ce4-b709-403a-824e-37072e227dc8&width=768&dpr=4&quality=100&sign=ca837904&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F50QZBbFzIooLL6SE2zdl%252FAWS%2520Environment%2520Setup.jpg%3Falt%3Dmedia%26token%3D6def2904-4c7a-4d52-b85c-b3b553cc5657&width=768&dpr=4&quality=100&sign=c822492f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F7iXR9KknebMfnhBcpvnC%252FAWS%2520Rotation%2520Hierarchy.jpg%3Falt%3Dmedia%26token%3Df1e1b0e0-5de4-4c1a-9a38-83877a59d289&width=768&dpr=4&quality=100&sign=14db5526&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGEDJmvpUaT8ImnYLgjLV%252FKeeperPAM%2520Configuration.jpg%3Falt%3Dmedia%26token%3D657572ec-45bc-4e1a-a219-2402c655252a&width=768&dpr=4&quality=100&sign=8009b119&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fes2MA1KVac2YXpHVcHp5%252FScreenshot%25202025-02-09%2520at%25208.48.45%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D75fb48b0-f924-4ffa-
aa22-4528c4b0977a&width=768&dpr=4&quality=100&sign=68db9d58&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FZEojWQmDX3MsE0EMlM1D%252FScreenshot%25202025-02-09%2520at%25208.49.59%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dd9740e18-2a6b-4ea9-b534-eb67addf8c97&width=768&dpr=4&quality=100&sign=e8aaaba2&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FETnLSTu5qYNj0xwMltI2%252FKeeperPAM%2520Machine.jpg%3Falt%3Dmedia%26token%3D7f69333a-8f02-410f-8542-1882216994b6&width=768&dpr=4&quality=100&sign=5324b381&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FYzn7xA4rI6mcsTSwW1pz%252FScreenshot%25202024-12-26%2520at%25205.30.05%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Da4e98fcc-37b0-4906-843e-b1bcd5bf5b4f&width=768&dpr=4&quality=100&sign=b27d3f5f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FHeovfKrm4CXGKwiIqq11%252FScreenshot%25202025-01-01%2520at%25209.27.18%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db4e0a075-94bf-43da-
aa25-bf684ab3a00d&width=768&dpr=4&quality=100&sign=68e0a16&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGfUUKJYQrvyHbjH6wLC9%252FScreenshot%25202025-01-01%2520at%25209.31.08%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dacd71242-e88f-4283-8aa9-7d68c5dd96ae&width=768&dpr=4&quality=100&sign=a74e0ae&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FrSy701IpEDZQukD6q7kh%252FScreenshot%25202025-01-01%2520at%25209.39.22%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D35cfb79d-a8b8-4e57-87b3-84921ab720d9&width=768&dpr=4&quality=100&sign=8b7fe257&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F3RtXTHeGIFJVRWtkORwj%252FScreenshot%25202025-01-01%2520at%25209.41.18%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3De3686b71-94f2-4d91-b43b-b7c9644142df&width=768&dpr=4&quality=100&sign=2573abaf&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGMWX8nti9YeFXKMsewLp%252FScreenshot%25202025-01-22%2520at%25208.22.52%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D65ceef4f-099d-48bb-b443-6c72568e2cf1&width=768&dpr=4&quality=100&sign=38313f83&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FD8nqAfaDPIW4WBCW9Rxr%252FScreenshot%25202025-01-22%2520at%25208.53.04%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D06fac322-b21d-4041-b023-bda02e7e509f&width=768&dpr=4&quality=100&sign=1fe67e18&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Ftds8AxVXgjBxUp62XOWO%252FScreenshot%25202025-01-22%2520at%25208.57.23%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3De5b51065-620f-4e11-8e95-565659691a5f&width=768&dpr=4&quality=100&sign=4197fecc&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FgJYt2F84PuVu30sU8vjA%252FScreenshot%25202025-01-22%2520at%25208.58.45%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D3510536e-e225-4627-b500-f131bd092e71&width=768&dpr=4&quality=100&sign=3fcd5b5e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FjzpPPcD5sRb1UohoCaTn%252FScreenshot%25202025-01-22%2520at%25202.39.35%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Da1847cd6-036a-43ca-a220-9221e9ce0e22&width=768&dpr=4&quality=100&sign=12e3e7c4&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FOqQstEohDohyhgqfligd%252FScreenshot%25202025-01-22%2520at%25209.00.02%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D38ae8843-15e6-4d46-b9f8-d0617f951f59&width=768&dpr=4&quality=100&sign=c5bc0f5f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FvTerkzM1KDDL2qOPHOiK%252FScreenshot%25202025-01-22%2520at%252011.31.29%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D7e389ee7-fb42-415e-af05-77edc52fb7b0&width=768&dpr=4&quality=100&sign=ebc8648a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F2PCBiJqbmG3n6wxDbnVC%252FScreenshot%25202025-01-22%2520at%252011.29.22%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D57cf7545-d924-40d3-ba82-d2522d2a1d35&width=768&dpr=4&quality=100&sign=914ec646&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FXKvhl56ubmEQ6TpG64OE%252FScreenshot%25202025-01-22%2520at%252011.35.08%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db8af7246-67d9-4fb1-b2d1-c163d0a62f35&width=768&dpr=4&quality=100&sign=dfab6c3a&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fa8jbmcsDeYYa47z9MSdN%252FScreenshot%25202025-01-22%2520at%252011.38.18%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D37816466-3bac-4567-9bdb-95f8c4af014c&width=768&dpr=4&quality=100&sign=3c9ddac8&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FRLKC4C4j0s9e9ls71mYB%252FScreenshot%25202025-01-22%2520at%252011.38.38%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D5d7dea1d-ee99-4060-a880-122f1c5c4a2a&width=768&dpr=4&quality=100&sign=8f88bd4c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FuV3f6t7N6GqqieotwmKW%252FScreenshot%25202025-01-22%2520at%252011.39.03%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Df35b94f4-8f73-4452-b426-d6320bae4cd8&width=768&dpr=4&quality=100&sign=87a055a7&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FG43gSJCEtSl4zWbGowLm%252FKeeperPAM%2520Database.jpg%3Falt%3Dmedia%26token%3D977d6327-73b4-4fa5-98cd-2783e905db39&width=768&dpr=4&quality=100&sign=9773dba2&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FafSL2rOYf5xNGoajV91A%252FScreenshot%25202024-12-28%2520at%25206.45.24%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dc517c017-ae7c-4b7e-8a1e-5b43aedac786&width=768&dpr=4&quality=100&sign=f60da786&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FHeovfKrm4CXGKwiIqq11%252FScreenshot%25202025-01-01%2520at%25209.27.18%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db4e0a075-94bf-43da-
aa25-bf684ab3a00d&width=768&dpr=4&quality=100&sign=68e0a16&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FQDnmwlO5pIBfiNFcSqJM%252FScreenshot%25202025-01-01%2520at%25209.48.44%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Df3cd398b-968e-4933-8a6d-7b1219374da4&width=768&dpr=4&quality=100&sign=8eea2be3&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FVSwnnpOvh75YONo6GSFD%252FScreenshot%25202025-01-01%2520at%25209.53.35%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D0bbbe72f-3230-4d03-98b7-71f52edd1469&width=768&dpr=4&quality=100&sign=ff984fa2&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FkAjqR7emtY9jLtKEyEkg%252FKeeperPAM%2520User.jpg%3Falt%3Dmedia%26token%3Db43bd7ce-e079-4e7e-aabc-592ef88f5e11&width=768&dpr=4&quality=100&sign=8e5923e6&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FIRM2u2catMzTjLm3TP6n%252FScreenshot%25202024-12-28%2520at%25207.44.54%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D39192e46-6bd5-44c1-90de-12e3a2f17a18&width=768&dpr=4&quality=100&sign=33e61a6b&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FLKQi1jLQWs8CA7EGR7eD%252FKeeperPAM%2520Remote%2520Browser.jpg%3Falt%3Dmedia%26token%3D711d7db0-b5c2-444f-bf89-5aa444dfbbf8&width=768&dpr=4&quality=100&sign=28beb448&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FSy3rZi1RT37UGJpbI4J1%252FScreenshot%25202024-12-28%2520at%25207.17.54%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D06802fd6-994b-4c65-a90e-2b93c61be56f&width=768&dpr=4&quality=100&sign=c273f521&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FlizxOCMg4atoYAjhS7WT%252FScreenshot%25202025-01-01%2520at%252010.00.03%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D4ae39ea2-59f3-427e-8128-98b5c6e56ec4&width=768&dpr=4&quality=100&sign=a846f439&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Flpcb27LMoJVaVdXPPdr1%252FScreenshot%25202025-01-01%2520at%252010.01.51%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dde3f3bad-c944-48f7-a6b0-c90d5657a31d&width=768&dpr=4&quality=100&sign=adca79a0&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FUIsmTVAwLmoexG3NzXB0%252FScreenshot%25202025-01-01%2520at%252010.02.08%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D8e5a073f-ca59-49ec-
ab23-11d960f192bb&width=768&dpr=4&quality=100&sign=a1f2454d&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FC08APnlcrl6pNYeGETKm%252FScreenshot%25202025-01-01%2520at%252010.05.23%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3De51ff4f5-13d6-4693-ba1c-3caf82dc010c&width=768&dpr=4&quality=100&sign=1eeb9c59&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FB5kDk5IAVTfFolQv0SHB%252FJust-
in-
time%2520access.jpg%3Falt%3Dmedia%26token%3Da90e3139-f25c-496d-b9de-8f8fa64bd644&width=768&dpr=4&quality=100&sign=9db1f8d7&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9iFf2XyKCvhd7CwXAN5c%252FJIT%2520ephemeral%2520account.png%3Falt%3Dmedia%26token%3Dc3275652-72b8-47da-b8a6-6d3efb88699a&width=768&dpr=4&quality=100&sign=c5fc4fe8&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fu8W0Y406cAePSP7Ds8Ph%252FJIT%2520Updated%2520-%2520Elevation.png%3Falt%3Dmedia%26token%3Dc23eecae-c7b9-480f-880a-df7ef7b9b0e3&width=768&dpr=4&quality=100&sign=d922cfcf&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FtT2ZNiogZn4kZ9tGexxp%252FRequests.png%3Falt%3Dmedia%26token%3D82c4148a-83b4-49e9-8716-502fe89884eb&width=768&dpr=4&quality=100&sign=e8689d0&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGk3XjDE5ORcq6Prd1lje%252FScreenshot%25202025-03-21%2520at%25209.29.03%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Da65b53e1-d7f3-44e5-9d33-d7654db7243e&width=768&dpr=4&quality=100&sign=f663d2ab&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FWkIRRG35dLvClY5Rnq4J%252FPAM%2520Settings%2520-%2520Workflow.png%3Falt%3Dmedia%26token%3De7d0e549-6267-40c8-bbcf-
cb929b534bc0&width=768&dpr=4&quality=100&sign=88359820&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FQr5fyjmlwXwVprNtTU9u%252FScreenshot%25202025-01-22%2520at%252011.30.35%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db7784f8c-cb10-40ed-8ad6-9da756e4cf9e&width=768&dpr=4&quality=100&sign=3c1d056c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FIbUtlOmj3Fv6V4EOFgcc%252FScreenshot%25202025-01-22%2520at%25202.35.24%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dff30fa4c-690e-44c8-a7ba-55d30b2a7aba&width=768&dpr=4&quality=100&sign=b06dcbd8&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F9TzdizFLhgX6rcOBZ2FS%252FScreenshot%25202025-01-22%2520at%25202.36.26%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3De7c5ae76-0c42-4540-b9f3-8779176a6090&width=768&dpr=4&quality=100&sign=eebb8bff&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FK5Tb4eWi4Z03NmYulgtf%252FScreenshot%25202025-01-22%2520at%25202.37.05%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D0895bb18-425c-479d-b1d0-56e44b89b05c&width=768&dpr=4&quality=100&sign=5601c4c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F5Uybk2vAImp3Vvv0tGsZ%252FScreenshot%25202025-01-22%2520at%25202.37.44%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dca15199c-2522-4926-a887-04c165bb91d7&width=768&dpr=4&quality=100&sign=92e14afc&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F1fXvbQXycfFNtIbPlKRb%252FScreenshot%25202025-01-22%2520at%25202.38.05%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D760f04e2-64fa-41fc-8a08-41446a757327&width=768&dpr=4&quality=100&sign=6050b3db&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FaEHM1ja8afZHkaJRCpav%252FKeeperPAM%2520Directory.jpg%3Falt%3Dmedia%26token%3Db99c8c27-4852-4e17-a09f-94527b83370e&width=768&dpr=4&quality=100&sign=95893222&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fbgi1mXTZeZNiLFj5n0yt%252FScreenshot%25202024-12-28%2520at%25207.15.08%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D496715e6-b203-4db3-b1df-
bdc0b5f89d7d&width=768&dpr=4&quality=100&sign=2d69951e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fo90ZxGpSTinflyYmV0kq%252FScreenshot%25202025-01-14%2520at%25209.18.43%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Db0f52b45-5050-40d4-8c14-4cd89c755259&width=768&dpr=4&quality=100&sign=b7c7af55&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FkmMyMNsM7zliUNYrl7Rc%252FScreenshot%25202025-01-14%2520at%25209.25.01%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D26d66869-50b0-4cdf-89d3-fc1b6c0d2fb0&width=768&dpr=4&quality=100&sign=da274de6&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FN889gw5Jl0rhnS1MqRsI%252FScreenshot%25202025-01-14%2520at%25209.15.20%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Df56979d9-6e19-4fc3-a1c6-15936bb6c512&width=768&dpr=4&quality=100&sign=3a9e809f&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fo3JZ3XsfotkypZRWXhGD%252FSharing%2520and%2520Access%2520Control.jpg%3Falt%3Dmedia%26token%3D09307a13-81b1-4c0b-b353-2b9704a1f7bf&width=768&dpr=4&quality=100&sign=63ddaeb&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FQpOPl4BgG78R5Dlly69T%252FScreenshot%25202025-05-26%2520at%25201.48.25%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D1516f192-a005-4bc3-8b44-d9dae4e7db80&width=768&dpr=4&quality=100&sign=c700a7de&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FRWbdYOqnrytlLo8KIVrc%252FScreenshot%25202024-12-29%2520at%25209.32.58%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D23bb2a5e-c32b-48c0-aa91-1475713c48ef&width=768&dpr=4&quality=100&sign=6c9f236e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fp3lGAjckjMuLTOr8ks7x%252FScreenshot%25202024-12-29%2520at%25209.31.41%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D4b396f38-e43e-44b5-9315-d01c773c8a3b&width=768&dpr=4&quality=100&sign=1af68525&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FdmgPLpJqmqpbpmQqdVPl%252FScreenshot%25202024-12-29%2520at%25209.40.58%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D3ec9a8f6-63c8-46fc-867d-6455b84b1af1&width=768&dpr=4&quality=100&sign=7b55da63&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FLUTiz0SYEVSdb9HSUHL1%252FScreenshot%25202024-12-29%2520at%252010.59.17%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D9c931196-46fa-44c0-a8e6-de7739f248e4&width=768&dpr=4&quality=100&sign=d88841ef&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FAQznDwDEokpAkogOXP4I%252FScreenshot%25202024-12-29%2520at%252011.04.23%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3Dc5d44aba-8c6e-40ac-8a29-a9fac70b5d6b&width=768&dpr=4&quality=100&sign=e1d5c650&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FrSJkj42udq93p4WQ8f0k%252FScreenshot%25202024-12-29%2520at%252012.04.07%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dab5e8ec8-968b-408d-93b3-4f560ceff388&width=768&dpr=4&quality=100&sign=9479cce0&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F4bUd1cwiF0FmzZs2JavY%252FScreenshot%25202024-12-29%2520at%252011.08.57%25E2%2580%25AFAM.png%3Falt%3Dmedia%26token%3D1e4e8967-d44e-41c1-aeed-54252ac8a34f&width=768&dpr=4&quality=100&sign=6ed67638&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FHjTtsmcWnXmBrSmYOJvx%252FScreenshot%25202024-12-29%2520at%252012.11.25%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Db7958c97-3f7b-4aff-8f4b-510bde522001&width=768&dpr=4&quality=100&sign=4464e6df&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FxVKiADDvqF1xKkxhT19g%252FScreenshot%25202024-12-29%2520at%252012.10.45%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D2e4833e7-9d5e-4bec-b9c7-e073003d2a5b&width=768&dpr=4&quality=100&sign=66cce91c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FyLIuHEMw6981YYXBB3BE%252FScreenshot%25202024-12-29%2520at%252012.18.03%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D2beee8fc-3b2a-4f9e-b50d-1cdf32bcb2ef&width=768&dpr=4&quality=100&sign=8ffdb783&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fw4x2k7YmPF0GIRSmbSCM%252FScreenshot%25202024-12-29%2520at%25208.16.03%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D71092ba4-9100-40aa-9707-4e60acf58e6e&width=768&dpr=4&quality=100&sign=6ee33659&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252Fr21NeuvUzV2M098yCdkS%252FScreenshot%25202024-12-29%2520at%25207.46.01%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Da1d04f7b-ee47-43c8-9883-5c6ff9f06f37&width=768&dpr=4&quality=100&sign=4666f2e7&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FKFtduQm5AbJCmSTCSdnh%252FScreenshot%25202024-12-29%2520at%252012.20.32%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dc872bbdf-f5cb-49b4-885d-f447bb0b4dfd&width=768&dpr=4&quality=100&sign=7efdc13e&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F0dgFjJlkmF8LsMC5klC8%252FScreenshot%25202024-12-29%2520at%252012.41.56%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Da4a57303-b642-402b-8120-9894d3ca1295&width=768&dpr=4&quality=100&sign=a6b733e9&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FM8MOOP4ezDWek1ARFCT9%252FScreenshot%25202024-12-29%2520at%252012.57.15%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D7d5387df-d443-4fbd-8f35-f45c277bd5c6&width=768&dpr=4&quality=100&sign=43584524&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FvpMHYlc5dYECZ6ZOUJzs%252FScreenshot%25202024-12-29%2520at%25205.34.43%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dc1984a44-96b0-4d8e-9c55-a2792317cf00&width=768&dpr=4&quality=100&sign=bb2497e8&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FP5lDpHHLKKd5HVvFIsZ5%252FScreenshot%25202024-12-29%2520at%25207.46.12%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D61132bac-
ded6-444f-8384-af8636715957&width=768&dpr=4&quality=100&sign=57657606&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FGloxaBWrEbb1dLDBPn3i%252FScreenshot%25202024-12-29%2520at%25208.21.39%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D78e55651-9464-476c-ad32-3b10a64242d2&width=768&dpr=4&quality=100&sign=97da3cfd&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FTDSctq3jorBX8Z92AdRW%252FScreenshot%25202024-12-29%2520at%25208.23.51%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3De3632323-d302-4a68-8fd1-e884de3fa928&width=768&dpr=4&quality=100&sign=212d246c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FhAKz204kkaYBMcjGqB7D%252FScreenshot%25202025-01-30%2520at%252010.11.31%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Dfd8439d7-d9bb-436b-a233-fc9f8110831c&width=768&dpr=4&quality=100&sign=472955b2&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FwYmcNZKRoL3p7QdpE5ik%252FAzure%2520Environment%2520Setup.jpg%3Falt%3Dmedia%26token%3D37c419f3-3638-4552-abb0-fdb5ded629b7&width=768&dpr=4&quality=100&sign=85396ef9&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FTn00oz3MsXcV6OU6XUZE%252FScreenshot%25202023-05-02%2520at%25201.49.35%2520PM.jpg%3Falt%3Dmedia%26token%3D146597ab-
caab-495c-9049-a4918e293dd2&width=768&dpr=4&quality=100&sign=d7862712&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F1VHxRugsu0DJAHvvbpI7%252FScreenshot%25202023-04-21%2520at%25203.57.27%2520PM.png%3Falt%3Dmedia%26token%3Df89c8cea-d345-417d-9b30-19008d1ee8ad&width=768&dpr=4&quality=100&sign=150ab5cd&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FW7lqqZ9KcqPA4WKUGug0%252FScreenshot%25202023-05-02%2520at%25201.54.45%2520PM.png%3Falt%3Dmedia%26token%3Dc03eefc3-fc29-483e-8319-d1867b1ce5d1&width=768&dpr=4&quality=100&sign=ab2d801c&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FsBqZQC7UtyX0xiKu4k0P%252FScreenshot%25202023-04-21%2520at%25203.11.54%2520PM.png%3Falt%3Dmedia%26token%3Dfdcb3152-1f28-43e8-a7bb-9d02ecfd04a1&width=768&dpr=4&quality=100&sign=b41d9daf&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252FyiFpVADjARBtRoRZE1YN%252FScreenshot%25202023-05-02%2520at%25202.01.34%2520PM.jpg%3Falt%3Dmedia%26token%3D23546bd6-443e-4048-8f92-c02fc1bbbe34&width=768&dpr=4&quality=100&sign=a7f7144&sv=2)

![](https://docs.keeper.io/~gitbook/image?url=https%3A%2F%2F762006384-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-
x-
prod.appspot.com%2Fo%2Fspaces%252F-MJXOXEifAmpyvNVL1to%252Fuploads%252F00jLNdtIDAnsmH2r7Zuj%252FScreenshot%25202023-05-02%2520at%25202.03.31%2520PM.jpg%3Falt%3Dmedia%26token%3D666817a0-78a5-40ec-9f86-9280f9116514&width=768&dpr=4&quality=100&sign=45e6743c&sv=2)

section

section

Note (1)

section

section

section

section

section

[`secrets-manager app
share`](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/commander-cli/command-
reference/secrets-manager-commands)

