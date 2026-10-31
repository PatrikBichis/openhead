# DisplayShow

**Title:** DisplayShow

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Change what fills the screen. `content` is named so to avoid clashing with the envelope's `type`. Images come as an http(s) URL the device fetches, or as a `data:image/...;base64,` URI under 1 MB. With `overlay: face-corner` the face keeps running in a corner.

| Property                       | Pattern | Type             | Deprecated | Definition                           | Title/Description                                                      |
| ------------------------------ | ------- | ---------------- | ---------- | ------------------------------------ | ---------------------------------------------------------------------- |
| + [type](#type )               | No      | const            | No         | -                                    | -                                                                      |
| + [content](#content )         | No      | enum (of string) | No         | In ../common.json#/$defs/view        | What fills the screen.                                                 |
| - [source](#source )           | No      | string           | No         | -                                    | Required for \`image\` and \`web\`. \`web\` accepts http(s) URLs only. |
| - [overlay](#overlay )         | No      | enum (of string) | No         | -                                    | Default \`none\`.                                                      |
| - [duration_ms](#duration_ms ) | No      | integer          | No         | In ../common.json#/$defs/duration_ms | Return to the face after this time. Omit to hold.                      |

| All of(Requirement)  |
| -------------------- |
| [Command](#allOf_i0) |
| [item 1](#allOf_i1)  |

## <a name="allOf_i0"></a>1. Property `DisplayShow > allOf > Command`

**Title:** Command

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | ../command.json  |

**Description:** Base for commands. Every command is answered with `ack` or `error` carrying the same `id`.

| Property                  | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| ------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#allOf_i0_type ) | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#allOf_i0_ts )     | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#allOf_i0_seq )   | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#allOf_i0_id )     | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                       |

### <a name="allOf_i0_type"></a>1.1. Property `DisplayShow > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `DisplayShow > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `DisplayShow > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_id"></a>1.4. Property `DisplayShow > allOf > Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="allOf_i1"></a>2. Property `DisplayShow > allOf > item 1`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

### <a name="autogenerated_heading_2"></a>2.1. If (content = null)

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

#### <a name="autogenerated_heading_3"></a>2.1.1. The following properties are required
* source

## <a name="type"></a>3. Property `DisplayShow > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"display.show"`

## <a name="content"></a>4. Property `DisplayShow > content`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `enum (of string)`         |
| **Required**   | Yes                        |
| **Defined in** | ../common.json#/$defs/view |

**Description:** What fills the screen.

Must be one of:
* "face"
* "image"
* "web"

## <a name="source"></a>5. Property `DisplayShow > source`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Required for `image` and `web`. `web` accepts http(s) URLs only.

| Restrictions                      |                                                                                                                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Max length**                    | 1400000                                                                                                                                                                                 |
| **Must match regular expression** | ```^(https?://\|data:image/(png\|jpeg\|gif\|webp);base64,)``` [Test](https://regex101.com/?regex=%5E%28https%3F%3A%2F%2F%7Cdata%3Aimage%2F%28png%7Cjpeg%7Cgif%7Cwebp%29%3Bbase64%2C%29) |

## <a name="overlay"></a>6. Property `DisplayShow > overlay`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default `none`.

Must be one of:
* "none"
* "face-corner"

## <a name="duration_ms"></a>7. Property `DisplayShow > duration_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/duration_ms |

**Description:** Return to the face after this time. Omit to hold.

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

----------------------------------------------------------------------------------------------------------------------------
