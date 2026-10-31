# SystemScreenshot

**Title:** SystemScreenshot

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** PNG of what is on screen. Dev mode only. With `delivery: url` the image is served by the device's HTTP server (WebSocket port + 1) for 60 s and must be fetched with the token in an `Authorization: Bearer` header.

| Property                 | Pattern | Type             | Deprecated | Definition | Title/Description                                            |
| ------------------------ | ------- | ---------------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#type )         | No      | string           | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )             | No      | integer          | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )           | No      | integer          | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#id )             | No      | string           | No         | -          | Client-chosen id, echoed in the reply.                       |
| - [scale](#scale )       | No      | number           | No         | -          | Fraction of native resolution. Default 1.                    |
| - [delivery](#delivery ) | No      | enum (of string) | No         | -          | Default \`url\`.                                             |

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

## <a name="id"></a>4. Property `Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="scale"></a>5. Property `SystemScreenshot > scale`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Fraction of native resolution. Default 1.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &gt; 0 |
| **Maximum**  | &le; 1 |

## <a name="delivery"></a>6. Property `SystemScreenshot > delivery`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default `url`.

Must be one of:
* "url"
* "inline"

----------------------------------------------------------------------------------------------------------------------------
