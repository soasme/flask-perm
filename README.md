Flask-Perm
----------

## Example

```python
perm = Perm()
perm.app = app
perm.init_app(app)

print perm.has_permission(user_id, 'product.add') # True

print perm.get_user_permissions(user_id) # ['product.add', 'product.update']

@perm.require_permission('product.delete') #  throw perm.Denied
def add_or_update_product(product_id):
    # do something

@app.errorhandler(perm.Denied)
def handle_perm_denied(e):
    return jsonify({msg: 'permission denied'}), 403
```
