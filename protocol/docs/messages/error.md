# Error

**Title:** Error

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Failed command (with `id`) or failed handshake (without).

| Property               | Pattern | Type             | Deprecated | Definition | Title/Description                                            |
| ---------------------- | ------- | ---------------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#type )       | No      | string           | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )           | No      | integer          | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )         | No      | integer          | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| - [id](#id )           | No      | string           | No         | -          | -                                                            |
| + [code](#code )       | No      | enum (of string) | No         | -          | -                                                            |
| + [message](#message ) | No      | string           | No         | -          | -                                                            |
| - [details](#details ) | No      | object           | No         | -          | -                                                            |

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

## <a name="id"></a>4. Property `Error > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="code"></a>5. Property `Error > code`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "unauthorized"
* "unsupported"
* "busy"
* "invalid_params"
* "dev_mode_required"
* "rate_limited"

## <a name="message"></a>6. Property `Error > message`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |      |
| -------------- | ---- |
| **Max length** | 1024 |

## <a name="details"></a>7. Property `Error > details`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

----------------------------------------------------------------------------------------------------------------------------
