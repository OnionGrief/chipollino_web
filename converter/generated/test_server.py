import concurrent.futures
import logging

import grpc

import converter_pb2
import converter_pb2_grpc


class GreeterServicer(converter_pb2_grpc.GreeterServicer):
    def getString(self, request, context):
        return converter_pb2.StringResponse(text="Привет из gRPC!")


def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    converter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
