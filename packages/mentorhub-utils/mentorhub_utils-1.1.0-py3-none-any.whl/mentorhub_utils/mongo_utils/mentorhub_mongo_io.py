import logging
import sys
from bson import ObjectId 
from pymongo import MongoClient
from mentorhub_utils.config.MentorHub_Config import MentorHub_Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: - Refactor to use connection pooling

class MentorHubMongoIO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MentorHubMongoIO, cls).__new__(cls, *args, **kwargs)
            cls._instance.connected = False
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.config = MentorHub_Config.get_instance()
        return cls._instance

    def configure(self, enumerators_collection_key):
        """Initialize Config values for Versions and Enumerators"""
        self.config = MentorHub_Config.get_instance()
        self._connect()
        self._load_versions()
        self._load_enumerators(enumerators_collection_key)
        
    def _connect(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.config.MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=2000, socketTimeoutMS=5000)
            # TODO: Config timeout
            self.client.admin.command('ping')  # Force connection
            self.db = self.client.get_database(self.config.MONGO_DB_NAME)
            self.connected = True
            logger.info(f"Connected to MongoDB")
        except Exception as e:
            logger.fatal(f"Failed to connect to MongoDB: {e} - exiting")
            sys.exit(1) # fail fast 

    def disconnect(self):
        """Disconnect from MongoDB."""
        if not self.connected: return
            
        try:
            if self.client:
                self.client.close()
                logger.info("Disconnected from MongoDB")
        except Exception as e:
            logger.fatal(f"Failed to disconnect from MongoDB: {e} - exiting")
            sys.exit(1) # fail fast 
      
    def _load_versions(self):
        """Load the versions collection into memory."""
        try:
            versions_collection_name = self.config.VERSION_COLLECTION_NAME
            self.config.versions = self.get_documents(versions_collection_name)
            print(f"Versions: {self.config.versions}")

            logger.info(f"{len(self.config.versions)} Versions Loaded.")
        except Exception as e:
            logger.fatal(f"Failed to get or load versions: {e} - exiting")
            sys.exit(1) # fail fast 

    def _load_enumerators(self, enumerators_collection_key):
        """Load the enumerators collection into memory."""
        if len(self.config.versions) == 0:
            logger.fatal("No Versions to load Enumerators from - exiting")
            sys.exit(1) # fail fast 
        
        try: 
            # Get the enumerators version from the curriculum version number.
            version_strings = [version['currentVersion'].split('.').pop() or "0" 
                for version in self.config.versions if version['collectionName'] == enumerators_collection_key]
            the_version_string = version_strings.pop() if version_strings else "0"
            the_version = int(the_version_string)

            # Query the database            
            
            enumerators_collection_name = self.config.ENUMERATORS_COLLECTION_NAME
            match = { "version": the_version }
            enumerations = self.get_documents(enumerators_collection_name, match)
    
            # Fail Fast if not found - critical error
            if not enumerations:
                logger.fatal(f"Enumerators not found for version: {self.config.ENUMERATORS_COLLECTION_NAME}:{the_version_string}")
                sys.exit(1) # fail fast 
    
            # Fail Fast if too many are found - it should be 1 document
            if len(enumerations) != 1:
                logger.fatal(f"{len(enumerations)} ! Too many Enumerators found for version: {the_version_string}")
                sys.exit(1) # fail fast 
    
            self.config.enumerators = enumerations[0]['enumerators']
            logger.info(f"{len(enumerations)} Enumerators Loaded.")
        except Exception as e:
            logger.fatal(f"Failed to get or load enumerators: {e} - exiting")
            sys.exit(1) # fail fast 

    def get_documents(self, collection_name, match=None, project=None, sort_by=None):
        """
        Retrieve a list of documents based on a match, projection, and optional sorting.

        Args:
            collection_name (str): Name of the collection to query.
            match (dict, optional): MongoDB match filter. Defaults to {}.
            project (dict, optional): Fields to include or exclude. Defaults to None.
            sort_by (list of tuple, optional): Sorting criteria (e.g., [('field1', ASCENDING), ('field2', DESCENDING)]). Defaults to None.

        Returns:
            list: List of documents matching the query.
        """
        if not self.connected:
            return None

        # Default match and projection
        match = match or {}
        project = project or None
        sort_by = sort_by or None

        try:
            collection = self.db.get_collection(collection_name)
            cursor = collection.find(match, project)
            if sort_by: cursor = cursor.sort(sort_by)

            documents = list(cursor)
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents from collection '{collection_name}': {e}")
            raise
                
    def get_document(self, collection_name, document_id):
        """Retrieve a document by ID."""
        if not self.connected: return None

        try:
            # Get the document
            collection = self.db.get_collection(collection_name)
            document_object_id = ObjectId(document_id)
            document = collection.find_one({"_id": document_object_id})
            return document
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise

    def create_document(self, collection_name, document):
        """Create a curriculum by ID."""
        if not self.connected: return None
        
        try:
            document_collection = self.db.get_collection(collection_name)
            result = document_collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise   

    def update_document(self, collection_name, document_id, data):
        """Update a encounter."""
        if not self.connected: return None

        try:
            document_collection = self.db.get_collection(collection_name)
            document_object_id = ObjectId(document_id)
            
            match = {"_id": document_object_id}
            pipeline = {"$set": data}            
            updated_count = document_collection.update_one(match, pipeline)
            
            if updated_count == 0:
                raise f"Document Not Found {document_id}"
        
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise 

        return self.get_document(collection_name, document_id)

    def delete_document(self, collection_name, document_id):
        """Delete a document."""
        if not self.connected: return None

        try:
            document_collection = self.db[collection_name]
            document_object_id = ObjectId(document_id)
            result = document_collection.delete_one({"_id": document_object_id})
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise 
        
        return result.deleted_count
    
    # Singleton Getter
    @staticmethod
    def get_instance():
        """Get the singleton instance of the MongoIO class."""
        if MentorHubMongoIO._instance is None:
            MentorHubMongoIO()
        return MentorHubMongoIO._instance
