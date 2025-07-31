# Copyright 2025 Jiaqi Liu. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from multiprocessing import Process

import load_ancient_greek
import load_german
import load_italian
import load_latin

if __name__ == "__main__":
    latin = Process(target=load_latin.load_into_database())
    italian = Process(target=load_italian.load_into_database())
    german = Process(target=load_german.load_into_database())
    ancient_greek = Process(target=load_ancient_greek.load_into_database())

    latin.start()
    italian.start()
    german.start()
    ancient_greek.start()

    latin.join()
    italian.join()
    german.join()
    ancient_greek.join()
