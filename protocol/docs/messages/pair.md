# Pair

**Title:** Pair

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Pairing attempt with the code shown on the device. Answered with `welcome`, or `error` with `unauthorized` (wrong code) or `rate_limited` (locked for five minutes after five failures).

| Property         | Pattern | Type    | Deprecated | Definition | Title/Description                                                    |
| ---------------- | ------- | ------- | ---------- | ---------- | -------------------------------------------------------------------- |
| + [type](#type ) | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.         |
| + [ts](#ts )     | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.                   |
| + [seq](#seq )   | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.                |
| + [code](#code ) | No      | string  | No         | -          | Devices show six digits; the simulator accepts \`0000\` in dev mode. |

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

## <a name="code"></a>4. Property `Pair > code`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Devices show six digits; the simulator accepts `0000` in dev mode.

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[0-9]{4,8}$``` [Test](https://regex101.com/?regex=%5E%5B0-9%5D%7B4%2C8%7D%24) |

----------------------------------------------------------------------------------------------------------------------------
