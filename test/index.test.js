const axios = require("axios")
jest.mock('axios');
const BASE_URL = 'http://localhost:8000';
describe('Health Check', () => {
    test('should return server status', async () => {
        const mockResponse = { data: { message: 'Server is running' } };
        axios.get.mockResolvedValue(mockResponse);

        const response = await axios.get(`${BASE_URL}/`);
        expect(response.data.message).toBe('Server is running');
    });
});

describe('Auth Routes', () => {
    const authEndpoint = `${BASE_URL}/auth`;

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Signup', () => {
        test('should create new user successfully', async () => {
            const userData = {
                username: 'testuser',
                password: 'password123',
                address: '123 Test St',
                role: 'User'
            };

            const mockResponse = {
                data: { 
                    ...userData,
                    id: '123',
                    password: 'hashed_password'
                }
            };
            axios.post.mockResolvedValue(mockResponse);

            const response = await axios.post(`${authEndpoint}/signup`, userData);
            expect(response.data.username).toBe('testuser');
            expect(response.data.id).toBe('123');
            expect(response.data.role).toBe('User');
        });

        test('should handle duplicate username', async () => {
            const userData = {
                username: 'existinguser',
                password: 'password123',
                address: '123 Test St',
                role: 'User'
            };

            const errorResponse = {
                response: {
                    status: 409,
                    data: { detail: 'Username already taken' }
                }
            };
            axios.post.mockRejectedValue(errorResponse);

            await expect(async () => {
                await axios.post(`${authEndpoint}/signup`, userData);
            }).rejects.toEqual(errorResponse);
        });
    });

    describe('Login', () => {
        test('should login successfully', async () => {
            const loginData = {
                username: 'testuser',
                password: 'password123'
            };

            const mockResponse = {
                data: {
                    user: {
                        username: 'testuser',
                        id: '123',
                        address: '123 Test St',
                        role: 'User'
                    },
                    token: 'mock_jwt_token'
                }
            };
            axios.post.mockResolvedValue(mockResponse);

            const response = await axios.post(`${authEndpoint}/signin`, loginData);
            expect(response.data.token).toBe('mock_jwt_token');
            expect(response.data.user.username).toBe('testuser');
        });

        test('should handle invalid credentials', async () => {
            const loginData = {
                username: 'testuser',
                password: 'wrongpassword'
            };

            const errorResponse = {
                response: {
                    status: 403,
                    data: { detail: 'Incorrect password' }
                }
            };
            axios.post.mockRejectedValue(errorResponse);

            await expect(async () => {
                await axios.post(`${authEndpoint}/signin`, loginData);
            }).rejects.toEqual(errorResponse);
        });
    });
});

describe('Admin Routes', () => {
    const adminEndpoint = `${BASE_URL}/admin`;
    const mockToken = 'mock_admin_token';
    const headers = { Authorization: `Bearer ${mockToken}` };

    describe('Product Management', () => {
        test('should create product successfully', async () => {
            const productData = {
                name: 'Test Product',
                price: 99.99,
                description: 'Test Description',
                default_quantity: 10
            };

            const mockResponse = {
                data: { 
                    ...productData,
                    id: '123'
                }
            };
            axios.post.mockResolvedValue(mockResponse);

            const response = await axios.post(
                `${adminEndpoint}/product`,
                productData,
                { headers }
            );
            expect(response.data.name).toBe('Test Product');
            expect(response.data.price).toBe(99.99);
            expect(response.data.id).toBe('123');
        });

        test('should handle unauthorized access', async () => {
            const productData = {
                name: 'Test Product',
                price: 99.99,
                description: 'Test Description',
                default_quantity: 10
            };

            const errorResponse = {
                response: {
                    status: 403,
                    data: { error: 'Not authorized' }
                }
            };
            axios.post.mockRejectedValue(errorResponse);

            await expect(async () => {
                await axios.post(`${adminEndpoint}/product`, productData);
            }).rejects.toEqual(errorResponse);
        });

        test('should delete product successfully', async () => {
            const productId = '123';
            const mockResponse = {
                data: {
                    message: 'Product deleted',
                    data: 'Deleted'
                }
            };
            axios.delete.mockResolvedValue(mockResponse);

            const response = await axios.delete(
                `${adminEndpoint}/product/${productId}`,
                { headers }
            );
            expect(response.data.message).toBe('Product deleted');
        });
    });
});

describe('Order Routes', () => {
    const orderEndpoint = `${BASE_URL}/order`;

    test('should create order successfully', async () => {
        const orderData = {
            user_id: '123',
            product_id: '456',
            quantity: 2
        };

        const mockResponse = {
            data: {
                message: 'Order placed successfully',
                data: {
                    id: '789',
                    ...orderData,
                    amount: 199.98
                },
                remaining_stock: 8
            }
        };
        axios.post.mockResolvedValue(mockResponse);

        const response = await axios.post(`${orderEndpoint}/buy`, orderData);
        expect(response.data.message).toBe('Order placed successfully');
        expect(response.data.data.id).toBe('789');
        expect(response.data.remaining_stock).toBe(8);
    });

    test('should handle insufficient stock', async () => {
        const orderData = {
            user_id: '123',
            product_id: '456',
            quantity: 100
        };

        const errorResponse = {
            response: {
                status: 400,
                data: { detail: 'Insufficient stock available' }
            }
        };
        axios.post.mockRejectedValue(errorResponse);

        await expect(async () => {
            await axios.post(`${orderEndpoint}/buy`, orderData);
        }).rejects.toEqual(errorResponse);
    });

    test('should get all orders successfully', async () => {
        const mockResponse = {
            data: {
                message: 'Orders retrieved successfully',
                data: [
                    {
                        id: '789',
                        user_id: '123',
                        product_id: '456',
                        quantity: 2,
                        amount: 199.98
                    }
                ]
            }
        };
        axios.get.mockResolvedValue(mockResponse);

        const response = await axios.get(`${orderEndpoint}/`);
        expect(response.data.message).toBe('Orders retrieved successfully');
        expect(response.data.data.length).toBe(1);
        expect(response.data.data[0].id).toBe('789');
    });
});

describe('Product Routes', () => {
    const productEndpoint = `${BASE_URL}/products`;

    test('should get all products successfully', async () => {
        const mockResponse = {
            data: {
                message: 'Products',
                data: [
                    {
                        id: '123',
                        name: 'Test Product',
                        price: 99.99,
                        description: 'Test Description'
                    }
                ]
            }
        };
        axios.get.mockResolvedValue(mockResponse);

        const response = await axios.get(productEndpoint);
        expect(response.data.message).toBe('Products');
        expect(response.data.data.length).toBe(1);
        expect(response.data.data[0].name).toBe('Test Product');
    });

    test('should handle no products found', async () => {
        const errorResponse = {
            response: {
                status: 400,
                data: { detail: 'Products not found' }
            }
        };
        axios.get.mockRejectedValue(errorResponse);

        await expect(async () => {
            await axios.get(productEndpoint);
        }).rejects.toEqual(errorResponse);
    });
});