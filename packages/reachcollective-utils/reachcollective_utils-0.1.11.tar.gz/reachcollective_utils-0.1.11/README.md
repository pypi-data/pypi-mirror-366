# ReachCollective / APIs / Utils
Utilities for developing RESTful API, Open API projects with FastAPI and Python

# Requirements
- sqlmodel (>=0.0.22,<0.0.23)
- fastapi (>=0.115.8,<0.116.0)
- pydantic (>=2.10.6,<3.0.0)

# Installation

### Poetry
```
poetry add reachcollective-utils
```
### Pip
```
pip install reachcollective-utils
```

# Components

## DataGrid
List and paginate data from a model, accepting filters, sorting, and relationships.

### 1. Modify models
Add `to_dict()` function to each SQL Model, `to_dict()` gets relationships.

```python

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str | None
    status: str | None
    comments: list["Comment"] | None = Relationship(back_populates="post", sa_relationship_kwargs={"lazy": "raise"})

    def to_dict(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if 'comments' in self.__dict__:
            data['comments'] = []
            if self.quota_groups:
                data['comments'] = [quota_group.to_dict(*args, **kwargs) for quota_group in self.quota_groups]

        return data


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    description: str | None
    post: Post | None = Relationship(back_populates="comments", sa_relationship_kwargs={"lazy": "raise"})

    def to_dict(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if 'post' in self.__dict__:
            data['post'] = {}
            if self.survey:
                data['post'] = self.survey.model_dump(*args, **kwargs)

        return data
 ```

### 2. Basic use
```python
# URL: /posts?sort=-created&filter[status]=active&view=paginate


from app.models import Post
from reachcollective.utils.datagrid import DataGrid

@router.get('/posts', status_code=HTTPStatus.OK)
async def list_(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    return await DataGrid(db, Post, request).init().get()
```

### 2. Custom filters
```python
# URL: /posts?sort=-created&filter[status]=active&filter[name]=demo&view=paginate


from app.models import Post
from reachcollective.utils.datagrid import DataGrid

@router.get('/posts', status_code=HTTPStatus.OK)
async def list_(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    datagrid = DataGrid(db, Post, request)
    datagrid.qp.filters.personalize = ['name']
    datagrid.init()

    for key, value in datagrid.params['filters']['customize'].items():
        match key:
            case 'name':
                datagrid.qb.stmt = datagrid.qb.stmt.where(Post.name.ilike(f'%{value}%'))

    return await datagrid.get()
 ```

### 3. Relationships
```python
# URL: /posts?sort=-created&filter[status]=active&view=paginate&with=comments


from app.models import Post
from reachcollective.utils.datagrid import DataGrid

@router.get('/posts', status_code=HTTPStatus.OK)
async def list_(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    return await DataGrid(db, Post, request).init().get()
```

### 4. Results
```json
{
  "current_page": 1,
  "data": [
    {
      "id": "18a6ac49-cb2f-41c7-ac14-ff5360210c65",
      "name": "demo",
      "status": "active"
    },
    {
      "id": "81f08423-288f-4e74-bcbb-edf5ef37f1fe",
      "name": "demo",
      "status": "active"
    },
    {
      "id": "a017c74f-f0bb-4f65-9faf-36581812bbe7",
      "name": "Test 4",
      "status": "active"
    }
  ],
  "total": 683,
  "per_page": 15,
  "total_pages": 46
}
```

```json
{
  "current_page": 1,
  "data": [
    {
      "id": "18a6ac49-cb2f-41c7-ac14-ff5360210c65",
      "name": "demo",
      "status": "active",
      "comments": [
        {
          "id": "28a6ac49-cb2f-41c7-ac14-ff5360210c15",
          "name": "Hello"
        },
        {
          "id": "38a6ac49-cb2f-41c7-ac14-ff5360210c25",
          "name": "World"
        }
      ]
    },
    {
      "id": "81f08423-288f-4e74-bcbb-edf5ef37f1fe",
      "name": "demo",
      "status": "active",
      "comments": []
    },
    {
      "id": "a017c74f-f0bb-4f65-9faf-36581812bbe7",
      "name": "Test 4",
      "status": "active",
      "comments": [
        {
          "id": "38a6ac49-cb2f-41c7-ac14-ff5360210c35",
          "name": "Hello"
        }
      ]
    }
  ],
  "total": 683,
  "per_page": 15,
  "total_pages": 46
}
```

## Query Params
Parses, sanitizes and formats data from a URL query params. NOTE: Does not require `sqlmodel`

```python
# URL: /query-params?sort=-last_updated&with=survey,profile&size=2&filter[name]=young&filter[status]=active|deactivate&filter[survey_id]=994c231c|8a900c77&view=paginate

from reachcollective.utils.datagrid import QueryParams
from reachcollective.utils import APIRender

@router.get('/query-params')
async def test_query_params(request: Request):
    try:
        return QueryParams(request).get()
    except HTTPException as e:
        return APIRender.error(e.detail, e.status_code)
```

### Results
```json
{
  "filters": {
    "init": {},
    "equals": {
      "name": "young",
      "status": [
        "active",
        "deactivate"
      ],
      "survey_id": [
        "994c231c",
        "8a900c77"
      ]
    },
    "customize": {}
  },
  "with": [
    "survey",
    "profile"
  ],
  "sort": [
    {
      "col": "last_updated",
      "dir": "desc",
      "by": "-last_updated"
    }
  ],
  "view": "paginate",
  "page": 1,
  "size": 2
}
```

## APIRender
Centralizes fastAPI and third-party responses into a single class. Used in FastaPI routes. NOTE: Require `pydantic`

```python
from reachcollective.utils import APIRender

@router.get('/api-render')
async def test_query_params(request: Request):
    try:
        # TODO: Your code here
    except HTTPException as e:
        return APIRender.error(e.detail, e.status_code)
```