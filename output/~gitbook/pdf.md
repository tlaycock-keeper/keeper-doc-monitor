[](https://docs.keeper.io/en/keeperpam/ "Go back to content")

[All pages](?limit=100)

[Powered by
GitBook](https://www.gitbook.com/?utm_source=content&utm_medium=trademark&utm_campaign=-MJXOXEifAmpyvNVL1to)

1 of 1

Loading...

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

[Secrets Manager CLI](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/secrets-manager-command-line-interface)

[Developer SDKs](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/developer-sdk-library)

[Integrations](https://app.gitbook.com/s/-MJXOXEifAmpyvNVL1to/secrets-
manager/integrations)

One-Time Access Token

Managing Applications

Creating a Shared Folder

Add Application to Shared Folder

Assigning a Gateway to an Application

Create a Gateway and associated applications

Gateway Creation Wizard

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

