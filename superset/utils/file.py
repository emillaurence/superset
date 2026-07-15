# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from typing import Optional

from werkzeug.utils import secure_filename


def get_filename(
    model_name: Optional[str], model_id: int, skip_id: bool = False
) -> str:
    # ``model_name`` may be missing for partially configured or migrated
    # assets (e.g. a chart without a ``slice_name``); fall back to the id
    # rather than failing the export.
    slug = secure_filename(model_name) if model_name else ""
    filename = slug if skip_id else f"{slug}_{model_id}"
    return filename if slug else str(model_id)
