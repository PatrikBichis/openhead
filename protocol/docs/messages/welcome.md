# Welcome

**Title:** Welcome

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Session accepted. Carries the client's token (new after pairing, unchanged on reconnect), the device description and what it supports.

| Property                                 | Pattern | Type            | Deprecated | Definition                       | Title/Description                                                                                                                                                                                |
| ---------------------------------------- | ------- | --------------- | ---------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| + [type](#type )                         | No      | string          | No         | -                                | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.                                                                                                                                     |
| + [ts](#ts )                             | No      | integer         | No         | -                                | Sender clock in milliseconds since the Unix epoch.                                                                                                                                               |
| + [seq](#seq )                           | No      | integer         | No         | -                                | Per-connection, per-direction counter, starting at 0.                                                                                                                                            |
| + [token](#token )                       | No      | string          | No         | -                                | -                                                                                                                                                                                                |
| + [protocol_version](#protocol_version ) | No      | string          | No         | In ../common.json#/$defs/version | Semantic version, MAJOR.MINOR.PATCH.                                                                                                                                                             |
| + [device](#device )                     | No      | object          | No         | In #/$defs/device                | -                                                                                                                                                                                                |
| + [capabilities](#capabilities )         | No      | array of string | No         | -                                | Feature flags. Known in 0.1: \`face\`, \`display.image\`, \`display.video\`, \`display.web\`, \`display.subtitle\`, \`imu\`, \`status\`, \`log\`, \`screenshot\`. Clients ignore unknown values. |
| + [themes](#themes )                     | No      | array           | No         | -                                | -                                                                                                                                                                                                |
| + [dev_mode](#dev_mode )                 | No      | boolean         | No         | -                                | -                                                                                                                                                                                                |

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

## <a name="token"></a>4. Property `Welcome > token`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |     |
| -------------- | --- |
| **Min length** | 16  |
| **Max length** | 256 |

## <a name="protocol_version"></a>5. Property `Welcome > protocol_version`

|                |                               |
| -------------- | ----------------------------- |
| **Type**       | `string`                      |
| **Required**   | Yes                           |
| **Defined in** | ../common.json#/$defs/version |

**Description:** Semantic version, MAJOR.MINOR.PATCH.

| Restrictions                      |                                                                                                                       |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[0-9]+\.[0-9]+\.[0-9]+$``` [Test](https://regex101.com/?regex=%5E%5B0-9%5D%2B%5C.%5B0-9%5D%2B%5C.%5B0-9%5D%2B%24) |

## <a name="device"></a>6. Property `Welcome > device`

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | Yes            |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/device |

| Property                              | Pattern | Type             | Deprecated | Definition        | Title/Description                         |
| ------------------------------------- | ------- | ---------------- | ---------- | ----------------- | ----------------------------------------- |
| + [name](#device_name )               | No      | string           | No         | -                 | -                                         |
| + [platform](#device_platform )       | No      | enum (of string) | No         | -                 | -                                         |
| + [model](#device_model )             | No      | string           | No         | -                 | Hardware identifier, e.g. \`iPhone13,2\`. |
| + [os_version](#device_os_version )   | No      | string           | No         | -                 | -                                         |
| + [app_version](#device_app_version ) | No      | string           | No         | -                 | -                                         |
| + [screen](#device_screen )           | No      | object           | No         | In #/$defs/screen | -                                         |

### <a name="device_name"></a>6.1. Property `Welcome > device > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

### <a name="device_platform"></a>6.2. Property `Welcome > device > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "ios"
* "ipados"
* "android"
* "sim"

### <a name="device_model"></a>6.3. Property `Welcome > device > model`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Hardware identifier, e.g. `iPhone13,2`.

### <a name="device_os_version"></a>6.4. Property `Welcome > device > os_version`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

### <a name="device_app_version"></a>6.5. Property `Welcome > device > app_version`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

### <a name="device_screen"></a>6.6. Property `Welcome > device > screen`

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | Yes            |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/screen |

| Property                                 | Pattern | Type   | Deprecated | Definition        | Title/Description           |
| ---------------------------------------- | ------- | ------ | ---------- | ----------------- | --------------------------- |
| + [width](#device_screen_width )         | No      | number | No         | -                 | Points.                     |
| + [height](#device_screen_height )       | No      | number | No         | -                 | Points.                     |
| + [scale](#device_screen_scale )         | No      | number | No         | -                 | -                           |
| + [safe_area](#device_screen_safe_area ) | No      | object | No         | In #/$defs/insets | Safe-area insets in points. |

#### <a name="device_screen_width"></a>6.6.1. Property `Welcome > device > screen > width`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

**Description:** Points.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &gt; 0 |

#### <a name="device_screen_height"></a>6.6.2. Property `Welcome > device > screen > height`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

**Description:** Points.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &gt; 0 |

#### <a name="device_screen_scale"></a>6.6.3. Property `Welcome > device > screen > scale`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &gt; 0 |

#### <a name="device_screen_safe_area"></a>6.6.4. Property `Welcome > device > screen > safe_area`

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | Yes            |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/insets |

**Description:** Safe-area insets in points.

| Property                                     | Pattern | Type   | Deprecated | Definition | Title/Description |
| -------------------------------------------- | ------- | ------ | ---------- | ---------- | ----------------- |
| + [top](#device_screen_safe_area_top )       | No      | number | No         | -          | -                 |
| + [left](#device_screen_safe_area_left )     | No      | number | No         | -          | -                 |
| + [bottom](#device_screen_safe_area_bottom ) | No      | number | No         | -          | -                 |
| + [right](#device_screen_safe_area_right )   | No      | number | No         | -          | -                 |

##### <a name="device_screen_safe_area_top"></a>6.6.4.1. Property `Welcome > device > screen > safe_area > top`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

##### <a name="device_screen_safe_area_left"></a>6.6.4.2. Property `Welcome > device > screen > safe_area > left`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

##### <a name="device_screen_safe_area_bottom"></a>6.6.4.3. Property `Welcome > device > screen > safe_area > bottom`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

##### <a name="device_screen_safe_area_right"></a>6.6.4.4. Property `Welcome > device > screen > safe_area > right`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="capabilities"></a>7. Property `Welcome > capabilities`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

**Description:** Feature flags. Known in 0.1: `face`, `display.image`, `display.video`, `display.web`, `display.subtitle`, `imu`, `status`, `log`, `screenshot`. Clients ignore unknown values.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be           | Description |
| ----------------------------------------- | ----------- |
| [capabilities items](#capabilities_items) | -           |

### <a name="capabilities_items"></a>7.1. Welcome > capabilities > capabilities items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions                      |                                                                                                 |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_.-]*$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_.-%5D%2A%24) |

## <a name="themes"></a>8. Property `Welcome > themes`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description                                         |
| ------------------------------- | --------------------------------------------------- |
| [name](#themes_items)           | Lower-case identifier used for themes and emotions. |

### <a name="themes_items"></a>8.1. Welcome > themes > name

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/name |

**Description:** Lower-case identifier used for themes and emotions.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

## <a name="dev_mode"></a>9. Property `Welcome > dev_mode`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | Yes       |

----------------------------------------------------------------------------------------------------------------------------
