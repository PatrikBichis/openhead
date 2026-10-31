# PairRequired

**Title:** PairRequired

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Sent by the device when `hello` has no valid token. The device shows a pairing code on screen.

| Property                           | Pattern | Type    | Deprecated | Definition                           | Title/Description                                             |
| ---------------------------------- | ------- | ------- | ---------- | ------------------------------------ | ------------------------------------------------------------- |
| + [type](#type )                   | No      | string  | No         | -                                    | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.  |
| + [ts](#ts )                       | No      | integer | No         | -                                    | Sender clock in milliseconds since the Unix epoch.            |
| + [seq](#seq )                     | No      | integer | No         | -                                    | Per-connection, per-direction counter, starting at 0.         |
| + [code_hint](#code_hint )         | No      | string  | No         | -                                    | Where to find the code, e.g. "6-digit code shown on head-01". |
| + [code_length](#code_length )     | No      | integer | No         | -                                    | -                                                             |
| + [expires_in_ms](#expires_in_ms ) | No      | integer | No         | In ../common.json#/$defs/duration_ms | -                                                             |
| + [attempts_left](#attempts_left ) | No      | integer | No         | -                                    | -                                                             |

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

## <a name="code_hint"></a>4. Property `PairRequired > code_hint`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Where to find the code, e.g. "6-digit code shown on head-01".

| Restrictions   |     |
| -------------- | --- |
| **Max length** | 128 |

## <a name="code_length"></a>5. Property `PairRequired > code_length`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 4 |
| **Maximum**  | &le; 8 |

## <a name="expires_in_ms"></a>6. Property `PairRequired > expires_in_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | Yes                               |
| **Defined in** | ../common.json#/$defs/duration_ms |

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

## <a name="attempts_left"></a>7. Property `PairRequired > attempts_left`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

----------------------------------------------------------------------------------------------------------------------------
