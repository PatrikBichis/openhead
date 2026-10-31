# Hello

**Title:** Hello

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** First message on a new connection. Without a valid token the device answers `pair_required`; with one it answers `welcome`. The major version must match the device's.

| Property                                 | Pattern | Type    | Deprecated | Definition                       | Title/Description                                                               |
| ---------------------------------------- | ------- | ------- | ---------- | -------------------------------- | ------------------------------------------------------------------------------- |
| + [type](#type )                         | No      | string  | No         | -                                | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.                    |
| + [ts](#ts )                             | No      | integer | No         | -                                | Sender clock in milliseconds since the Unix epoch.                              |
| + [seq](#seq )                           | No      | integer | No         | -                                | Per-connection, per-direction counter, starting at 0.                           |
| + [client](#client )                     | No      | string  | No         | -                                | Human-readable client name, shown on the pairing screen and in the client list. |
| + [protocol_version](#protocol_version ) | No      | string  | No         | In ../common.json#/$defs/version | Semantic version, MAJOR.MINOR.PATCH.                                            |
| - [token](#token )                       | No      | string  | No         | -                                | Token from an earlier \`welcome\`.                                              |

## <a name="type"></a>1. Property `Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

## <a name="ts"></a>2. Property `Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="seq"></a>3. Property `Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="client"></a>4. Property `Hello > client`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Human-readable client name, shown on the pairing screen and in the client list.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="protocol_version"></a>5. Property `Hello > protocol_version`

|                |                               |
| -------------- | ----------------------------- |
| **Type**       | `string`                      |
| **Required**   | Yes                           |
| **Defined in** | ../common.json#/$defs/version |

**Description:** Semantic version, MAJOR.MINOR.PATCH.

| Restrictions                      |                                                                                                                       |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[0-9]+\.[0-9]+\.[0-9]+$``` [Test](https://regex101.com/?regex=%5E%5B0-9%5D%2B%5C.%5B0-9%5D%2B%5C.%5B0-9%5D%2B%24) |

## <a name="token"></a>6. Property `Hello > token`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Token from an earlier `welcome`.

| Restrictions   |     |
| -------------- | --- |
| **Min length** | 16  |
| **Max length** | 256 |

----------------------------------------------------------------------------------------------------------------------------
