import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from src.dhisana.utils.test_connect import test_connectivity


class TestConnectivity(unittest.TestCase):
    def test_jinaai_dispatch(self):
        async def runner():
            with patch('src.dhisana.utils.test_connect.test_jinaai', new=AsyncMock(return_value={'success': True, 'status_code': 200, 'error_message': None})):
                tool_config = [
                    {
                        'name': 'jinaai',
                        'configuration': [
                            {'name': 'apiKey', 'value': 'dummy'}
                        ]
                    }
                ]
                result = await test_connectivity(tool_config)
                self.assertIn('jinaai', result)
                self.assertTrue(result['jinaai']['success'])
        asyncio.run(runner())

    def test_firecrawl_dispatch(self):
        async def runner():
            with patch('src.dhisana.utils.test_connect.test_firecrawl', new=AsyncMock(return_value={'success': True, 'status_code': 200, 'error_message': None})):
                tool_config = [
                    {
                        'name': 'firecrawl',
                        'configuration': [
                            {'name': 'apiKey', 'value': 'dummy'}
                        ]
                    }
                ]
                result = await test_connectivity(tool_config)
                self.assertIn('firecrawl', result)
                self.assertTrue(result['firecrawl']['success'])
        asyncio.run(runner())


if __name__ == '__main__':
    unittest.main()
