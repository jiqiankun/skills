# 安全规约

## 输入验证

### 用户输入验证
- 隶属于用户个人的页面或者功能必须进行权限控制校验
- 用户敏感数据禁止直接展示，必须对展示数据进行脱敏
- 用户输入的 SQL 参数严格使用参数绑定或者 METADATA 字段值限定，防止 SQL 注入，禁止字符串拼接 SQL 访问数据库
- 用户请求传入的任何参数必须做有效性验证
- 禁止向 HTML 页面输出未经安全过滤或未正确转义的用户数据

### 参数校验
- 在使用平台资源，譬如短信、邮件、电话、下单、支付，必须实现正确的防重放的机制
- 发贴、评论、发送即时消息等用户生成内容的场景必须实现防刷、文本内容违禁词过滤等风控策略

## 数据安全

### 敏感信息处理
- 用户输入的 SQL 参数严格使用参数绑定或者 METADATA 字段值限定，防止 SQL 注入
- 在使用平台资源，譬如短信、邮件、电话、下单、支付，必须实现正确的防重放的机制

### 密码安全
- 用户密码必须使用加密存储，禁止明文存储
- 密码重置必须验证用户身份

## SQL 注入防护

### 参数绑定
```java
// 正确：使用参数绑定
String sql = "SELECT * FROM user WHERE user_name = ?";
PreparedStatement ps = connection.prepareStatement(sql);
ps.setString(1, userName);

// 错误：字符串拼接
String sql = "SELECT * FROM user WHERE user_name = '" + userName + "'";
```

### MyBatis 防注入
```xml
<!-- 正确：使用 #{} 参数绑定 -->
<select id="selectByUserName" resultMap="BaseResultMap">
    SELECT * FROM user WHERE user_name = #{userName}
</select>

<!-- 错误：使用 ${} 字符串拼接 -->
<select id="selectByUserName" resultMap="BaseResultMap">
    SELECT * FROM user WHERE user_name = '${userName}'
</select>
```


## 权限控制

### 接口权限校验
```java
// 使用 SaCheckPermission 注解
@SaCheckPermission("system:user:list")
@GetMapping("/admin/users")
public List<User> listUsers() {
    return userService.listAll();
}

    @SaCheckPermission("system:user:remove")
@DeleteMapping("/users/{id}")
public void deleteUser(@PathVariable Long id) {
    userService.deleteById(id);
}
```

### 数据权限控制
```java
// 确保用户只能访问自己的数据
public Order getOrder(Long orderId, Long userId) {
    Order order = orderDao.selectById(orderId);
    if (order == null) {
        throw new NotFoundException("订单不存在");
    }
    if (!order.getUserId().equals(userId)) {
        throw new ForbiddenException("无权访问该订单");
    }
    return order;
}
```




